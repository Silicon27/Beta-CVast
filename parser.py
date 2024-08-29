from vast_tokenizer import ConvertToToken
import ast
import sys, os

keywords = ["print", "use", "pyfunc", '"', "'", "(", ")", ":", ";", ",", "[", "]"]
tokens = ["PRINT", "USE", "PYFUNC", '"', "'", "(", ")", ":", ";", ",", "[", "]"]

file = "test.vast"

symbol = ["{", "}", "(", ")", ":", ";", ",", "[", "]"]

tokenize = ConvertToToken(keywords, file, tokens, symbol)
tokenized_output, tokenized_dict, tokenized_output_w_spaces = tokenize.tokenize()

print(tokenized_output)
print(tokenized_dict)
print(tokenized_output_w_spaces)

# _____________________________________________________________
# Note: Important Variables
# _____________________________________________________________

variables = {}
imported_python_functions = []


# _____________________________________________________________
#  NOTE: DEFINING PARSER CLASS:
# _____________________________________________________________

class Parser:
    def __init__(self, func):
        self.func = func

    def __call__(self, text, pos=0):
        return self.func(text, pos)

    def __repr__(self):
        return f"Parser: {self.func.__name__}()"


def seq(*parsers):
    def parse_seq(s, idx):
        result = []
        for parser in parsers:
            x, idx = parser(s, idx)
            if x is None:
                return None, idx
            result.append(x)
        return result, idx

    return Parser(parse_seq)


def fmap(f, parser):
    def inner(s, idx):
        x, idx = parser(s, idx)
        if x is None:
            return None, idx
        return f(x), idx

    return Parser(inner)


def pure(x):
    def inner(s, idx):
        return x, idx

    return Parser(inner)


# _____________________________________________________________
#  NOTE: OTHER IMPORTANT FUNCTIONS:
# _____________________________________________________________

def get_function_names(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.read()

    tree = ast.parse(file_contents)
    function_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    return function_names


# _____________________________________________________________
#  NOTE: DEFINING PARSERS FOR EACH TOKEN:
# _____________________________________________________________


def convert_to_evaluable(text, pos):
    pass
    for t in tokenized_output[pos:]:
        if t in variables["name"]:
            return t, pos + 1
        return t, pos + 1


def print_parser(text, pos):
    if pos < len(text) and text[pos] == "PRINT":
        return "PRINT", pos + 1
    return None, pos


def use_parser(text, pos):
    if pos < len(text) and text[pos] == "USE":
        return "USE", pos + 1
    return None, pos


def if_parser(text, pos):
    if pos < len(text) and text[pos] == "IF":
        return "IF", pos + 1
    return None, pos

def pyfunc_parser(text, pos):
    if pos < len(text) and text[pos] == "PYFUNC":
        return "PYFUNC", pos + 1
    return None, pos

def string_parser(text, pos, tquote):
    pos += 1  # Move past the quote
    message: str = ""
    while pos < len(text) and text[pos] != tquote:
        message += tokenized_output_w_spaces[pos]
        pos += 1
    return message, pos + 1  # Moved past the closing quote


def lbracket_parser(text, pos):
    if pos < len(text) and text[pos] == "(":
        return "(", pos + 1
    return None, pos


def rbracket_parser(text, pos):
    if pos < len(text) and text[pos] == ")":
        return ")", pos + 1
    return None, pos


def lsbracket_parser(text, pos):
    if pos < len(text) and text[pos] == "[":
        return "[", pos + 1
    return None, pos


def rsbracket_parser(text, pos):
    if pos < len(text) and text[pos] == "]":
        return "]", pos + 1
    return None, pos


def colon_parser(text, pos):
    if pos < len(text) and text[pos] == ":":
        return ":", pos + 1
    return None, pos


def value_parser(text, pos):
    if pos < len(text) and text[pos] == '"' or text[pos] == "'":
        return string_parser(text, pos, text[pos])
    else:
        return convert_to_evaluable(text, pos)


def condition_parser(text, pos, end):
    condition = ""
    while pos < len(text) and text[pos] != end:
        condition += tokenized_output_w_spaces[pos]
        pos += 1
    if eval(condition):
        return True, pos + 1  # Move past the "end" symbol
    if eval(condition) is not bool:
        return "Error", pos + 1
    return condition, pos + 1  # Move past the "end" symbol


def exec_py_parser(text, pos):
    try:
        global imported_python_functions
        imported_python_functions = get_function_names(f"{text[pos]}.py")
        return text[pos], pos + 1
    except Exception as e:
        print(f"Error executing {text[pos]}.py: {e}")
        return None, pos + 1

def list_parser(text, pos):
    values = []
    while text[pos] != "]":
        value, pos = value_parser(text, pos)
        if value is None:
            break
        values.append(value)
        if pos < len(text) and text[pos] == ",":
            pos += 1  # Skip the comma
        else:
            break
    return values, pos


def py_function_name_parser(text, pos):
    print(imported_python_functions)
    if pos < len(text) and text[pos] in imported_python_functions:
        return text[pos], pos + 1
    return None, pos


# _____________________________________________________________
#  NOTE: DEFINING SYNTAX FOR ALL STATEMENTS:
# _____________________________________________________________


print_syntax = seq(print_parser, lbracket_parser, value_parser, rbracket_parser)
if_syntax = seq(if_parser, lbracket_parser, condition_parser, rbracket_parser)
use_parser = seq(use_parser, exec_py_parser)
pyfunc_syntax = seq(pyfunc_parser, py_function_name_parser, colon_parser,
                    lsbracket_parser, list_parser, rsbracket_parser)

position: int = 0


# _____________________________________________________________
#  NOTE: RUN FUNCTIONS:
# _____________________________________________________________

filename = ""
def run_use(contents):
    global filename
    filename = contents

def run_pyfunc(contents):
    args_string = ""
    func = ""
    for item in contents:
        if item in imported_python_functions:
            func = item
        if isinstance(item, list):
            for i in item:
                if isinstance(i, str):
                    args_string += f'"{i}"'
                elif isinstance(i, int):
                    args_string += f"{i}"
                else:
                    raise ValueError(f"Invalid argument type: {type(i)}")
                if len(item) != 1:
                    args_string += ", "
    with open(f"{func}.py", "a+") as sfile:
        sfile.write(f"from {filename} import {func}\n")
        sfile.write(f"{func}({args_string})\n")
    os.system(f"python {func}.py")
    os.remove(f"{func}.py")

def run():
    global position
    while position < len(tokenized_output):
        if tokenized_output[position] == "PRINT":
            message, position = print_syntax(tokenized_output, position)
            print(message)
        elif tokenized_output[position] == "USE":
            message, position = use_parser(tokenized_output, position)
            run_use(message[1])
        elif tokenized_output[position] == "PYFUNC":
            message, position = pyfunc_syntax(tokenized_output, position)
            print(message)
            run_pyfunc(message)
        else:
            if tokenized_output[position] in imported_python_functions:
                position += 1


run()



run()


