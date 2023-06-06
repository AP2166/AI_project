import json 
from code_to_readable import PARSED_SNIPPETS

class Model:
    def __init__(self) -> None:
        self.table = {}

    def train(self, file):
        f = open(file)
        lines = f.readlines()

        for coll in lines[:1000]:
            item = json.loads(coll)
            self.create_chain(item[0], item)

    def test():
        pass

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

    def save_model(self):
        json_object = json.dumps(self.table, indent = 4)
        with open("trained_150k_v2_online.json", "w") as outfile:
            outfile.write(json_object)

    def read_model(self):
        with open("trained_150k_v2.json", "r") as read_content:
            table = json.load(read_content)
            self.table = table

    def get_top(self, key):
        if key in self.table:
            return list(map(lambda x: x if x[0] not in PARSED_SNIPPETS else PARSED_SNIPPETS[x[0]], sorted(self.table[key].items(), key=lambda x: x[1],  reverse=True)))

    def get_percentages(self):
        percent_tables = {}

        for item, val in self.table.items():
            total = sum(map(lambda x: x[1], val.items()))
            percentages = {k: v/total for k, v in val.items()}
            percent_tables[item] = percentages

        return percent_tables
