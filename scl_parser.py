import json

# Define constants for token types
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

# List of keywords in the SCL language
KEYWORDS = [DISPLAY, IF, THEN, ENDIF, FUNCTION, IS, ENDFUN, PARAMETERS, INTEGER, FLOAT, CHAR, NOT]

# Parser class
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = None
        self.token_index = 0

    # Retrieve the next token from the token list, skipping EOLs
    def get_next_token(self):
        while self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
            self.token_index += 1
            if self.current_token[0] != "<EOL>":  # Skip EOL tokens
                break
        else:
            self.current_token = ("EOF", "EOF")

    # Check if the identifier already exists in the symbol table
    def identifier_exists(self, identifier):
        return identifier in self.symbol_table

    # Start the parsing process
    def begin(self):
        self.symbol_table = {}
        self.get_next_token()
        self.statements()

    # Ensure the current token matches the expected type. If it does, move to the next token
    def match(self, expected_token_type):
        if self.current_token and self.current_token[0] == expected_token_type:
            self.get_next_token()
        else:
            raise SyntaxError(f"Expected {expected_token_type}, but found {self.current_token[0]} with value '{self.current_token[1]}' at position {self.token_index}")

    # Parse a sequence of statements until a specific token is found
    def statements(self):
        while self.current_token and self.current_token[0] not in ["ENDIF", "ELSE", "ENDFUN", "EOF"]:
            self.statement()

    def statement(self):
        # Handling variable assignment, array assignment, or function call
        if self.current_token[0] == IDENTIFIER:
            identifier = self.current_token[1]
            self.match(IDENTIFIER)
            if self.current_token[0] == EQUOP:
                self.match(EQUOP)
                # If the next token represents a function, parse a function call
                if self.current_token[0] == IDENTIFIER and self.tokens[self.token_index][0] == LP:
                    self.function_call()
                else:
                    self.expression()
            # Handle array assignment
            elif self.current_token[0] == LB:
                self.array_def()
                self.match(EQUOP)
                self.expression()
            else:
                raise SyntaxError(f"Invalid statement: {identifier}")
        
        # Parse a DISPLAY statement
        elif self.current_token[0] == DISPLAY:
            self.match(DISPLAY)
            self.expression_list()

        # Parse an IF-THEN-ELSE or IF-THEN statement
        elif self.current_token[0] == IF:
            self.match(IF)
            self.condition()
            self.match(THEN)
            self.statements()
            if self.current_token[0] == "ELSE":  # Check for ELSE clause
                self.match("ELSE")
                self.statements()
            self.match(ENDIF)
        
        # Parse a FUNCTION definition
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

    # Parse an array definition which is enclosed between LB (left bracket) and RB (right bracket)
    def array_def(self):
        self.match(LB)
        self.expression()
        self.match(RB)

    # Parse an arithmetic expression that can include addition, subtraction, multiplication, or division
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

    # Parse a term which can be an identifier, a signed or unsigned constant, a parenthesized expression, or a function call
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

    # Parse a list of expressions separated by commas
    def expression_list(self):
        self.expression()
        while self.current_token[0] == COMMA:
            self.match(COMMA)
            self.expression()

    # Parse a condition, which can be an expression or a NOT followed by another condition
    def condition(self):
        if self.current_token[0] == NOT:
            self.match(NOT)
            self.condition()
        else:
            self.expression()
            self.match(RELOP)
            self.expression()

    # Parse the PARAMETERS keyword if present and then parse the parameter list
    def parameters(self):
        if self.current_token[0] == PARAMETERS:
            self.match(PARAMETERS)
            self.param_list()

    # Parse a list of parameters for a function
    def param_list(self):
        self.match(IDENTIFIER)
        self.match(OF)
        self

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

    # Parse a function call
    def function_call(self):
        self.match(IDENTIFIER)
        self.parguments()

    # Parse a list of arguments for a function call
    def parguments(self):
        self.match(LP)
        self.expression_list()
        self.match(RP)

# Main function to execute the parser.
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
