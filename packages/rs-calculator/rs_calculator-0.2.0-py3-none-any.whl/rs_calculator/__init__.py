import re
from asteval import Interpreter

safe_eval = Interpreter()

def calculate(expression):
    """
    Safely evaluate a mathematical expression string.
    Supports +, -, *, /, //, %, **, parentheses, and multiple numbers.
    """
    expression = expression.replace("x", "*").replace("^", "**")

    if not re.fullmatch(r"[0-9+\-*/%^().\s]+", expression):
        return "Error: Invalid characters in expression"

    try:
        result = safe_eval(expression)
        if safe_eval.error:
            # Clear errors for next call
            safe_eval.error = []
            return "Error: Invalid expression"
        return result
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception:
        return "Error: Invalid expression"


def show_help():
    print(
        "How to use:\n"
        " Pass a math expression as a string to rs_calculator.calculate()\n"
        "Examples:\n"
        ' calculate(\"2 + 3 * (4 - 1)\")\n'
        ' calculate(\"5 ^ 2 + 10\")\n\n'
        "Supported operators: +, -, *, x, /, //, %, **, ^, ()\n"
        "Supports parentheses and complex expressions\n"
        "https://github.com/Rasa8877/rs-calculator\n"
        "Contact me: letperhut@gmail.com\n"
        "RS Calculator - simplest calculator library in Python!"
    )

__version__ = "0.2.0"
