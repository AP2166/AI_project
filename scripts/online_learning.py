import json

test = dict()

import ast
import json

from project import parse_ast
from parse import parse_file
from code_to_readable import PARSED_SNIPPETS
from parse_user_input import parse_user_input


class AutoComplete():
    def __init__(self):
        self.table = {}
        self.lines = ""
        self.value2types = {}
        self.types2values = {}
        self.namespaces = {}

    # CREATES A LOCAL COLLECTION TO LEARN FROM
    def log_values(self, base, curr_val):
        if 'children' in base and 'value' in base:
            for child in base['children']:
                if 'value' in child:
                    if base['value'] in self.namespaces:
                        self.namespaces[base['value']].append(child['value'])
                    else:
                        self.namespaces[base['value']] = [child['value']]

    def create_chain(self, base, coll, indexed=True):
        if 'children' in base:
            for child in base['children']:
                # self.table[base['type'], coll[children]['type']] = self.table.get(
                #     (base['type'], coll[children]['type']), 0) + 1
                if indexed:
                    child_item = coll[child]
                else:
                    child_item = child
                if base['type'] in self.table:
                    if coll[child]['type'] in self.table[base['type']]:
                        self.table[base['type']][child_item['type']] += 1
                    else:
                        self.table[base['type']][child_item['type']] = 1
                else:
                    self.table[base['type']] = {
                        child_item['type']: 1
                    }

                self.create_chain(child_item, coll)

    def get_percentages(self):
        percent_tables = {}

        for item, val in self.table.items():
            total = sum(map(lambda x: x[1], val.items()))
            percentages = {k: v / total for k, v in val.items()}
            percent_tables[item] = percentages

        return percent_tables

    def train(self, file):
        f = open(file)
        lines = f.readlines()
        # what is happening in the next line?? why is it limited to 1000 lines?
        for coll in lines:
            item = json.loads(coll)
            self.create_chain(item[0], item)

    def generate_types_values(self, tree):
        tree = json.loads(tree)

        for item in tree:
            self.value2types['value'] = item['type']

            if self.value2types['value'] not in self.types2values['type']:
                self.types2values['value'].append(self.value2types['value'])

    def generate_ast(self):
        tree = None

        tree = parse_file(self.lines)

        return tree
        # self.generate_types_values(tree)

    def get_top(self, key):
        if key in self.table:
            return list(map(lambda x: x if x[0] not in PARSED_SNIPPETS else PARSED_SNIPPETS[x[0]],
                            sorted(self.table[key].items(), key=lambda x: x[1], reverse=True)))

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
        elif "return" in text:
            return text, "Return"
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
            # return text.replace(":", ""), "Conditional"

        return text, None

    def listen(self):
        print("Suggestions: ", self.get_top('Module'))
        user_input = ""
        while True:
            input_var = input()
            # check if the user is done with the input
            if input_var == "exit":
                break
            parsed, key = self.parse_func_call(input_var)

            # self.lines += parsed + "\n"
            self.lines += input_var + "\n"
            user_input += input_var + "\n"

            if input_var[-1] != " ":
                last = {'type': key}

                if not key:
                    tree = self.generate_ast()
                    last = json.loads(tree)[-1]

                print('Current type: ',
                      last['type'], " Suggestions: ", self.get_top(last['type']))

        try:
            with open("user_input.json", "w") as f:
                f.write(parse_user_input(user_input))
            a.train("user_input.json")

            json_object = json.dumps(self.table, indent=4)

            with open("online_learning_table_full.json", "w") as outfile:
                outfile.write(json_object)
            print("Online learning successful! Table saved to online_learning_table_full.json")
        except Exception as e:
            print("Online learning failed")
            print(e)


a = AutoComplete()

with open("../trained_150k_v2.json", "r") as read_content:
    table = json.load(read_content)
    a.table = table

a.listen()
