import glob
import pickle
import json

from ast_utils import dfs
from ast_utils import NonTerminal
from ast_utils import transform_ast
from astroid import parse
"""
This Python file is used to play around with parsing and flat mapping of AST files. 
"""


def parse_asts_from_directory(directory, dump_to_disk=False):
    files = glob.glob(directory + "/*.py", recursive=True)
    print(files)
    for file in files:
        parse_ast(file).tree().visualize()


def parse_ast(content):

    ast = transform_ast(parse(content), file="data/test.pl")
    return ast.to_dict()
