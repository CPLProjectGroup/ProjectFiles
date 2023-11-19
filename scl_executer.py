import json
import argparse
skipline = 0

def analyze(line_of_code, context):
    global skipline 
    """
    Modified function to analyze and execute or display a line of code.
    - Handles various operations like variable assignment, arithmetic operations, list creation, display, and list element display.
    """
    
    #Checking if line ends an IF Statment
    if 'ENDIF' in line_of_code:
        skipline = 0
        return
    
    #Checking if skipline is enabled
    if skipline == 1:
        return

    # Skip empty lines
    if not line_of_code.strip():
        return

    # Logs which line is being executed
    print(f"Executing line: {line_of_code}")

    # Split the line into tokens
    tokens = line_of_code.split()

    #Handle IF Statements
    if 'IF' in line_of_code and 'THEN' in line_of_code:
        # Find the positions of 'IF' and 'THEN'
        start = line_of_code.find('IF') + len('IF')
        end = line_of_code.find('THEN')

        # Extract the condition and strip any leading/trailing whitespace
        condition = line_of_code[start:end].strip()

        # Evaluate the condition
        try:
            # Evaluate the condition
            if not eval(condition,context):
                skipline = 1
                return
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            
            
    # String Literal assignments
    if len(tokens) >= 3 and '"' in tokens[2]:
        context[tokens[0]] = tokens[2].replace('"', '')
        for token in tokens[3:]:
            context[tokens[0]] += ' ' + token.replace('"', '')


    # DISPLAY String Literal
    if len(tokens) > 3 and tokens[0] == 'DISPLAY' and type(tokens[1]) == str and '[' not in tokens and ',' not in tokens:
        value = tokens[1].replace('"', '')
        for token in tokens[2:]:
            value += " " + token.replace('"','')   
        print(value)
        return

    # Handling list creation and modification: Identifier[Integer] = Identifier[Integer] op Integer
    if len(tokens) == 11 and tokens[6] == '[':
        #First List
        list_name = tokens[0]
        index = tokens[2]
        idex = int(index)

        #Second List
        list_name2 = tokens[5]
        index2 = tokens[7]
        idex2 = int(index2)

        #Operation and last integer
        ops = ['+','-','/','*']
        op = tokens[9]
        number = tokens[10]
        
        # Check if the lists exists, if not, create it
        if list_name not in context:
            context[list_name] = []

        if list_name2 not in context:
            context[list_name2] = []

        # Generate the code and execute it
        context[list_name][idex] = eval(f'{context[list_name][idex2]} {op} {number}')
        print(context[list_name][idex])


    # Handling list creation and modification: Identifier[Integer] = Identifier
    if len(tokens) == 6 and tokens[1] == '[' and tokens[3] == ']' and tokens[4] == '=':
        list_name = tokens[0]
        index = tokens[2]
        value_identifier = tokens[5]

        # Check if list exists, if not, create it
        if list_name not in context:
            context[list_name] = []

        # Check if the value identifier exists and treat index as an integer
        if value_identifier in context:
            try:
                # Convert index to integer and insert the value
                idx = int(index)
                value = context[value_identifier]
                # Ensure the list is large enough
                while len(context[list_name]) <= idx:
                    context[list_name].append(0)
                context[list_name][idx] = value
            except ValueError:
                print(f"Error: Index '{index}' is not a valid integer")
        else:
            print(f"Error: Identifier '{value_identifier}' not found")

    # Handling display of list elements: DISPLAY Identifier[Integer]
    elif len(tokens) == 5 and tokens[0] == 'DISPLAY' and tokens[2] == '[' and tokens[4] == ']':
        identifier = tokens[1]
        index = tokens[3]

        if identifier in context and isinstance(context[identifier], list):
            try:
                # Convert index to integer and display the value
                idx = int(index)
                if idx < len(context[identifier]):
                    print(f"{identifier}[{idx}] = {context[identifier][idx]}")
                else:
                    print(f"Error: Index '{idx}' out of range for list '{identifier}'")
            except ValueError:
                print(f"Error: Index '{index}' is not a valid integer")
        else:
            print(f"Error: Identifier '{identifier}' not found or is not a list")

    # Handling assignment: Identifier = Unsigned Integer / Integer
    if len(tokens) == 3 and tokens[1] == '=':
        try:
            # Check if the third token is an integer
            int(tokens[2])

            # Execute the assignment
            exec(line_of_code, context)
        except ValueError:
            # If the third token is not an integer, skip the line
            print(f"Line skipped: {line_of_code}")

    # Handling arithmetic operations: Identifier = Identifier Operator Identifier
    elif len(tokens) == 5 and tokens[1] == '=' and tokens[3] in ['+', '-', '/', '*']:
        try:
            # Construct the operation expression
            operation = f"{tokens[2]} {tokens[3]} {tokens[4]}"
            # Execute the operation and assignment
            exec(f"{tokens[0]} = {operation}", context)
        except Exception as e:
            print(f"Error in executing arithmetic operation: {e}")

    # Handling display: DISPLAY Identifier [, Identifier...]
    elif tokens[0] == 'DISPLAY' and '[' not in tokens:
        for token in tokens[1:]:
            # Remove any commas and white spaces
            identifier = token.replace(',', '').strip()
            if identifier and identifier in context:
                print(f"{identifier} = {context[identifier]}")
            elif identifier:
                print(f"Identifier '{identifier}' not found")


def process_tokens(data):
    """
    Processes the tokens from the JSON data to construct and analyze lines of code.
    """

    current_line = []
    context = {}  # Initialize a context dictionary to store variable assignments
    
    for token in data:
        if token[0] == '<EOL>':
            line_of_code = ' '.join([t[1] for t in current_line])
            analyze(line_of_code, context)  # Pass the context dictionary to analyze
            current_line = []
        else:
            current_line.append(token)


def main(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    process_tokens(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a JSON file of code tokens.')
    parser.add_argument('file', type=str, help='Path to the JSON file containing code tokens')
    args = parser.parse_args()
    main(args.file)
