import json
import argparse

def evaluate_condition(condition, context):
    try:
        return eval(condition, {}, context)  # Use context as local variables for eval
    except Exception as e:
        print(f"Error evaluating condition '{condition}': {e}")
        return False

def analyze(line_of_code, context):
    """
    Modified function to analyze and execute or display a line of code.
    - Handles various operations like variable assignment, arithmetic operations, list creation, display, and list element display.
    """
    if not line_of_code.strip() or context["__skip_until"]:
        return

    tokens = line_of_code.split()
    
    
    #Handling If Statement
    if tokens[0] == 'IF':
        #Evaluate Condition within IF statement
        condition = ' '.join(tokens[1:-1])
        # Set execution flag based on true value
        context["__execute"] = evaluate_condition(condition, context)
        #Indicate inside if-then-else block
        context["__in_if_block"] = True
        context["__skip_else"] = context["__execute"]  # Skip ELSE block if THEN is executed
        return
    #Handling 'ELSE' statement
    elif tokens[0] == 'ELSE':
        #If THEN block was executed set execute flag to false to skip ELSE block
        if context["__skip_else"]:
            context["__execute"] = False  # Skip execution in ELSE block
        #If THEN block was not executed invert flag to execute ELSE block
        else:
            context["__execute"] = not context["__execute"]
        return
    # Handling ENDIF
    elif tokens[0] == 'ENDIF':
        # Reset if-then-else flags
        context["__in_if_block"] = False
        context["__skip_else"] = False
        #Reset execute flag to true
        context["__execute"] = True
        return
    # Skip execution of the line if we are inside an if-then-else block AND the execution flag is set to False
    if context.get("__in_if_block") and not context.get("__execute"):
        return

    print(f"Executing line: {line_of_code}")

   
    # String Literal assignments
    if tokens[1] == '=' and type(tokens[2]) == str:
        context[tokens[0]] = tokens[2].replace('"', '')
        for token in tokens[3:]:
            context[tokens[0]] += ' ' + token.replace('"', '')
        

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

    
def process_tokens(data, context):
    """
    Processes the tokens from the JSON data to construct and analyze lines of code.
    """
    current_line = []
    
    for token in data:
        if token[0] == '<EOL>':
            line_of_code = ' '.join([t[1] for t in current_line])
            analyze(line_of_code, context)  # Pass the context dictionary to analyze
            current_line = []
        else:
            current_line.append(token)


def main(file_path):
    context = {
        "__if_state": None, "__skip_until": None}
    with open(file_path, 'r') as file:
        data = json.load(file)
    process_tokens(data, context)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a JSON file of code tokens.')
    parser.add_argument('file', type=str, help='Path to the JSON file containing code tokens')
    args = parser.parse_args()
    main(args.file)
