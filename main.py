import json

from AI_project.scripts.parse import parse_file
from model import Model

class AutoComplete():
    def __init__(self):
        self.table = {}
        self.lines = ""
        self.value2types = {}
        self.types2values = {}
        self.namespaces = {}

    def _log_values(self, namespace, value):
        if namespace in self.namespaces:
            self.namespaces[namespace].append(value)
        else:
            self.namespaces[namespace] = [value]

    # CREATES A LOCAL COLLECTION TO LEARN FROM
    def log_values(self, base, coll, namespace):

        if base['type'] == 'Assign': 
            first_child = coll[base['children'][0]]

            if first_child['type'] == 'NameStore' and first_child['value'] != None:
                    self._log_values(namespace, first_child['value'])

            self.log_values(coll[base['children'][1]], coll, first_child['value'])

        elif base['type'] == 'Dict' and base['children']: 
            children_len = int(len(base['children'])/2)

            for child in base['children'][:children_len]:
                self._log_values(namespace, coll[child]['value'])
                self.log_values(coll[child + children_len], coll, coll[child]['value'])

        else: 
            if 'children' in base:
                for child in base['children']:
                    self.log_values(coll[child], coll, namespace)

    def generate_types_values(self, tree):
        tree = json.loads(tree)

        for item in tree:
            self.value2types['value'] = item['type']

            if self.value2types['value'] not in self.types2values['type']:
                self.types2values['value'].append(self.value2types['value'])

    def generate_ast(self):
        tree = None
        
        tree = parse_file(self.lines)
        parsed_tree = json.loads(tree)
        self.log_values(parsed_tree[0], parsed_tree, '*')
        print(self.namespaces)

        return tree

    @staticmethod
    def parse_func_call(text):
        """
        Parses incomplete code
        Parses the text to see if it is a function call, attribute load, assignment
        or a conditional, for loop or while loop
        :param text:
        :return:
        """
        if text[-1] == "(":
            return text.replace("(", ""), 'Call'
        elif text[-1] == ".":
            return text.replace(".", ""), "AttributeLoad"
        elif text[-1] == "=":
            return text.replace("=", ""), "Assign"
        elif text[-1] == " ":
            pass
        elif text[-1] == ":":
            # check if it is a for loop, while loop or conditional, or a function or class definition
            if text[:2] == "if":
                return text.replace(":", ""), "If"
            elif text[:3] == "for":
                return text.replace(":", ""), "For"
            elif text[:5] == "while":
                return text.replace(":", ""), "While"
            elif text[:3] == "def":
                return text.replace(":", ""), "FunctionDef"
            elif text[:5] == "class":
                return text.replace(":", ""), "ClassDef"
            #return text.replace(":", ""), "Conditional"

        return text, None

    def listen(self, model: Model):
        while True:
            input_var = input()
            parsed, key = self.parse_func_call(input_var)

            self.lines += parsed + "\n"

            if (input_var[-1] != " "):
                last = {'type': key}

                if not key:
                    tree = self.generate_ast()
                    print('generated tree', tree)
                    last = json.loads(tree)[-1]
                suggestions = model.get_top(last['type'])

                if suggestions:
                    suggestions = list(map(lambda key:  (*key, self.namespaces.get('*', [])) if key[0] == 'NameStore' else key, suggestions))

                print('Current type: ',
                      last['type'], " Suggestions: ", suggestions)
                

if __name__=="__main__":
    a = AutoComplete()
    m = Model()

    #m.train("data/python50k_eval.json")
    m.read_model()

    a.listen(m)
