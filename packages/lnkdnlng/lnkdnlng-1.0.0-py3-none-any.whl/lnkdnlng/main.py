import argparse
from language.errors import LexerError, ParseError, RuntimeError
from language.interpreter import Interpreter
from language.lexer import Lexer
from language.parser import Parser

def interpret(source_code: str):
    """
    Tokenize, parse, and execute the source code.
    """
    try:
        #   lexing
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
    #    token to tree
        parser = Parser(tokens)
        ast = parser.parse()
        
    #     interpretation
        interpreter = Interpreter()
        interpreter.interpret(ast)
    except (LexerError, ParseError, RuntimeError) as e:
        print(f"An Error Occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run the linkedin language interpreter.")
    parser.add_argument("file", help="Path to the source code file to interpret.")
    args = parser.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as file:  
            source_code = file.read()
        interpret(source_code)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
    except UnicodeDecodeError as e:
        print(f"Error: Unable to read file '{args.file}' - {e}")

if __name__ == "__main__":
    main()