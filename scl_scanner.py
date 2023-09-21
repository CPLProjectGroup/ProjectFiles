import re
import json

# Keywords and token types
KEYWORDS = ["DISPLAY", "IF", "THEN", "ENDIF", "FUNCTION", "IS", "ENDFUN", "PARAMETERS", "INTEGER", "FLOAT", "CHAR", "NOT"]
TOKEN_TYPES = [
    ("IDENTIFIER", r"\b[A-Za-z_][A-Za-z0-9_]*\b"),
    ("UNSIGNICON", r"\b\d+\b"),
    ("SIGNICON", r"[-+]?\b\d+\b"),
    ("PLUS", r"\+"),
    ("MINUS", r"\-"),
    ("STAR", r"\*"),
    ("DIVOP", r"[^(//)\"][0-9A-Za-z]*/[0-9A-Za-z]*"),
    ("EQUOP", r"="),
    ("RELOP", r"(==|!=|<|<=|>|>=)"),
    ("LB", r"\["),
    ("RB", r"\]"),
    ("LP", r"\("),
    ("RP", r"\)"),
    ("COMMA", r","),
    ("OF", r"OF")
]

def tokenize(source_code):
    tokens = []
    position = 0
    while position < len(source_code):
        match = None
        for token_type, pattern in TOKEN_TYPES:
            regex = re.compile(pattern)
            match = regex.match(source_code, position)
            if match:
                token_value = match.group(0)
                if token_type == "IDENTIFIER" and token_value in KEYWORDS:
                    tokens.append((token_value, token_value))
                else:
                    tokens.append((token_type, token_value))
                position = match.end()
                break
        
        if not match:
            position += 1

    return tokens

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python scl_scanner.py <filename>")
        return

    with open(sys.argv[1], 'r') as f:
        source_code = f.read()

    tokens = tokenize(source_code)
    for token in tokens:
        print(token)

    with open("tokens.json", "w") as outfile:
        json.dump(tokens, outfile)

if __name__ == "__main__":
    main()
