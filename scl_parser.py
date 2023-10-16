import json

# Constants for token types
IDENTIFIER = "IDENTIFIER"
UNSIGNICON = "UNSIGNICON"
SIGNICON = "SIGNICON"
PLUS = "PLUS"
MINUS = "MINUS"
STAR = "STAR"
DIVOP = "DIVOP"
EQUOP = "EQUOP"
RELOP = "RELOP"
LB = "LB"
RB = "RB"
LP = "LP"
RP = "RP"
COMMA = "COMMA"
OF = "OF"
DISPLAY = "DISPLAY"
IF = "IF"
THEN = "THEN"
ENDIF = "ENDIF"
FUNCTION = "FUNCTION"
IS = "IS"
ENDFUN = "ENDFUN"
PARAMETERS = "PARAMETERS"
INTEGER = "INTEGER"
FLOAT = "FLOAT"
CHAR = "CHAR"
NOT = "NOT"
STRING_LITERAL = "STRING_LITERAL"


# List of keywords and token types
KEYWORDS = [DISPLAY, IF, THEN, ENDIF, FUNCTION, IS, ENDFUN, PARAMETERS, INTEGER, FLOAT, CHAR, NOT]

# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = 0

    def get_next_token(self):
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1
        else:
            self.current_token = ("EOF", "EOF")


    def identifier_exists(self, identifier):
        return identifier in self.symbol_table

    def begin(self):
        self.symbol_table = {}
        self.get_next_token()
        self.statements()

    def match(self, expected_token_type):
        if self.current_token and self.current_token[0] == expected_token_type:
            self.get_next_token()
        else:
            raise SyntaxError(f"Expected {expected_token_type}, but found {self.current_token[0]} with value '{self.current_token[1]}' at position {self.token_index}")


    # Grammar rules
    def statements(self):
        while self.current_token and self.current_token[0] not in ["ENDIF", "ELSE", "ENDFUN", "EOF"]:
            self.statement()


    def statement(self):
        if self.current_token[0] == IDENTIFIER:
            identifier = self.current_token[1]
            self.match(IDENTIFIER)
            if self.current_token[0] == EQUOP:
                self.match(EQUOP)
                if self.current_token[0] == IDENTIFIER and self.tokens[self.token_index][0] == LP:
                    self.function_call()
                else:
                    self.expression()
            elif self.current_token[0] == LB:
                self.array_def()
                self.match(EQUOP)
                self.expression()
            else:
                raise SyntaxError(f"Invalid statement: {identifier}")
        elif self.current_token[0] == DISPLAY:
            self.match(DISPLAY)
            self.expression_list()
        elif self.current_token[0] == IF:
            self.match(IF)
            self.condition()
            self.match(THEN)
            self.statements()
            if self.current_token[0] == "ELSE":  # Check for ELSE clause
                self.match("ELSE")
                self.statements()
            self.match(ENDIF)
        elif self.current_token[0] == FUNCTION:
            self.match(FUNCTION)
            identifier = self.current_token[1]
            self.match(IDENTIFIER)
            self.parameters()
            self.match(IS)
            self.statements()
            self.match(ENDFUN)
            if self.current_token[1] != identifier:
                raise SyntaxError(f"Expected {identifier}, but found {self.current_token[0]} with value '{self.current_token[1]}' at position {self.token_index}")
            self.match(IDENTIFIER)
        else:
            raise SyntaxError(f"Unexpected token: {self.current_token[0]}")




    def array_def(self):
        self.match(LB)
        self.expression()
        self.match(RB)

    def expression(self):
        self.term()
        while self.current_token and self.current_token[0] in [PLUS, MINUS, STAR, DIVOP]:
            if self.current_token[0] == PLUS:
                self.match(PLUS)
            elif self.current_token[0] == MINUS:
                self.match(MINUS)
            elif self.current_token[0] == STAR:
                self.match(STAR)
            elif self.current_token[0] == DIVOP:
                self.match(DIVOP)
            self.term()


    def term(self):
        if self.current_token[0] == IDENTIFIER:
            self.match(IDENTIFIER)
            if self.current_token and self.current_token[0] == LB:  # Check for array reference
                self.array_def()
        elif self.current_token[0] in [UNSIGNICON, SIGNICON]:
            self.match(self.current_token[0])
        elif self.current_token[0] == LP:
            self.match(LP)
            self.expression()
            self.match(RP)
        elif self.current_token[0] == FUNCTION:
            self.function_call()
        elif self.current_token[0] == STRING_LITERAL:  # Handling string literals
            self.match(STRING_LITERAL)
        else:
            raise SyntaxError(f"Invalid term: {self.current_token[0]}")



    def expression_list(self):
        self.expression()
        while self.current_token[0] == COMMA:
            self.match(COMMA)
            self.expression()

    def condition(self):
        if self.current_token[0] == NOT:
            self.match(NOT)
            self.condition()
        else:
            self.expression()
            self.match(RELOP)
            self.expression()

    def parameters(self):
        if self.current_token[0] == PARAMETERS:
            self.match(PARAMETERS)
            self.param_list()
        # No else part required, since ε means do nothing

    def param_list(self):
        self.match(IDENTIFIER)
        self.match(OF)
        self.data_type()
        while self.current_token[0] == COMMA:
            self.match(COMMA)
            self.match(IDENTIFIER)
            self.match(OF)
            self.data_type()

    def data_type(self):
        if self.current_token[0] in [INTEGER, FLOAT, CHAR]:
            self.match(self.current_token[0])
        else:
            raise SyntaxError(f"Invalid data type: {self.current_token[0]}")

    def function_call(self):
        self.match(IDENTIFIER)
        self.parguments()

    def parguments(self):
        self.match(LP)
        self.expression_list()
        self.match(RP)


def main():
    with open("tokens.json", "r") as infile:
        tokens = json.load(infile)

    parser = Parser(tokens)
    try:
        parser.begin()
        print("Parsing successful. The input follows the subset of the SCL language grammar.")
    except SyntaxError as e:
        print(f"SyntaxError: {str(e)}")

if __name__ == "__main__":
    main()
