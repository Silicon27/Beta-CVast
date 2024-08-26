from vast_tokenizer import ConvertToToken

keywords = ["print", '"', "'", "(", ")"]
tokens = ["PRINT", '"', "'", "(", ")"]

file = "test.vast"

symbol = ["{", "}", "(", ")"]

tokenize = ConvertToToken(keywords, file, tokens, symbol)
tokenized_output, tokenized_dict, tokenized_output_w_spaces = tokenize.tokenize()

print(tokenized_output)
print(tokenized_dict)
print(tokenized_output_w_spaces)

# _____________________________________________________________
# Note: Important Variables
# _____________________________________________________________

variables = {}


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


def if_parser(text, pos):
    if pos < len(text) and text[pos] == "IF":
        return "IF", pos + 1
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

# _____________________________________________________________
#  NOTE: DEFINING SYNTAX FOR ALL STATEMENTS:
# _____________________________________________________________


print_syntax = seq(print_parser, lbracket_parser, value_parser, rbracket_parser)
if_syntax = seq(if_parser, lbracket_parser, condition_parser, rbracket_parser)


position: int = 0


# _____________________________________________________________
#  NOTE: RUN FUNCTION:
# _____________________________________________________________

def run():
    global position
    while position < len(tokenized_output):
        print(f" output {tokenized_output[position]}")
        if tokenized_output[position] == "PRINT":
            print(print_syntax(tokenized_output, position))
            message, position = print_syntax(tokenized_output, position)
            print(message)


run()


