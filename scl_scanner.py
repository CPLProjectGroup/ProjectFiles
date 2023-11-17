import re
import json

# Define Keywords and token types
KEYWORDS = ["DISPLAY", "IF", "THEN", "ENDIF", "FUNCTION", "IS", "ENDFUN", "PARAMETERS", "INTEGER", "FLOAT", "CHAR", "NOT"]
TOKEN_TYPES = [
    ("OF", r"OF"),                                          # Of Keyword
    ("IDENTIFIER", r"\b[A-Za-z_][A-Za-z0-9_]*\b"),          # Alphanumeric Identifier
    ("UNSIGNICON", r"\b\d+\b"),                             # Unsigned integers
    ("SIGNICON", r"[-+]?\b\d+\b"),                          # Signed integers
    ("PLUS", r"\+"),                                        # Addition Operator
    ("MINUS", r"\-"),                                       # Subtraction Operator
    ("STAR", r"\*"),                                        # Multiplication Operator
    ("DIVOP", r"[^(//)\"][0-9A-Za-z]*/[0-9A-Za-z]*"),       # Division Operator
    ("EQUOP", r"="),                                        # Assignment Operator
    ("RELOP", r"(==|!=|<=|>=|<|>)"),                        # Relational Operators
    ("LB", r"\["),                                          # Left Bracket 
    ("RB", r"\]"),                                          # Right Bracket    
    ("LP", r"\("),                                          # Left Parenthesis
    ("RP", r"\)"),                                          # Right Parenthesis
    ("COMMA", r","),                                        # Comma
    ("STRING_LITERAL", r"\".*?\"")                          # String literals
]

# Function to tokenize the source code
def tokenize(source_code):
    tokens = []  # list to store tokens
    position = 0  # Initialize Position in source code
    # loop through the source code for tokenization
    while position < len(source_code):
        if source_code[position] == '\n':  # Check for newline character
            tokens.append(("<EOL>", "<EOL>"))
            position += 1
            continue

        match = None
        # loop through each token type and its corresponding regex pattern
        for token_type, pattern in TOKEN_TYPES:
            regex = re.compile(pattern)
            match = regex.match(source_code, position)
            # if match append to tokens list
            if match:
                token_value = match.group(0)
                if token_type == "IDENTIFIER" and token_value in KEYWORDS:
                    tokens.append((token_value, token_value))
                else:
                    tokens.append((token_type, token_value))
                position = match.end()
                break
        # if no match is found increment position
        if not match:
            position += 1

    return tokens  # returns the list of tokens

# Main function to execute the program
def main():
    import sys
    if len(sys.argv) != 2: # check for the correct number of command line arguments
        print("Usage: python scl_scanner.py <filename>")  
        return
    # read source code from file
    with open(sys.argv[1], 'r') as f:
        source_code = f.read()
    # tokenize source code
    tokens = tokenize(source_code)
    # print each token
    for token in tokens:
        print(token)
    # Save tokens to JSON
    with open("tokens.json", "w") as outfile:
        json.dump(tokens, outfile)

if __name__ == "__main__":
    main()
