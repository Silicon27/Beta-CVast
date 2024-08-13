from tokenize import ConvertToToken

keywords = ["print", '"', "'", "(", ")"]
tokens = ["PRINT", '"', "'", "(", ")"]

file = "test.vast"

symbol = ["{", "}", "(", ")"]

tokenize = ConvertToToken(keywords, file, tokens, symbol)
tokenized_output, tokenized_dict, tokenized_output_w_spaces = tokenize.tokenize()

print(tokenized_output)


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
                return (None, idx)
            result.append(x)
        return result, idx

    return Parser(parse_seq)


def print_parser(text, pos):
    if text == "PRINT":
        return "PRINT", pos + 1
    return None, pos

def string_parser(text, pos):
    if text == '"':
        return '"', pos + 1
    return None, pos

def run():
    for token in tokenized_output:
        pass # Completing this tomorrow 

