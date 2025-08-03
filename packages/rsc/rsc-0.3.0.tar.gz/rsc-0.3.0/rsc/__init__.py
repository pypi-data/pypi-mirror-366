import re
import math
from asteval import Interpreter

# Symbol table with constants and math functions
symbol_table = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "sqrt": math.sqrt,
    "factorial": math.factorial,
}

def replace_factorial(expr):
    # Replace e.g. 5! or var! with factorial(...)
    return re.sub(r"(\b\w+\b)!", r"factorial(\1)", expr)

def replace_operators(expr):
    expr = expr.replace("^", "**")
    # Replace 'x' or 'X' between digits or parentheses with '*'
    expr = re.sub(r"(?<=\d|\))\s*[xX]\s*(?=\d|\()", "*", expr)
    expr = replace_factorial(expr)
    return expr

def assign_var(name, value):
    if not name.isidentifier():
        return "Error: Invalid variable name"
    symbol_table[name] = value

def calculate(expression):
    expression = replace_operators(expression)
    aeval = Interpreter(symtable=symbol_table, use_numpy=False)
    aeval.error = []  # reset errors

    try:
        result = aeval(expression)
        if aeval.error:
            err = aeval.error[0]
            err_type = type(err.exc).__name__ if err.exc else "Error"
            err_msg = str(err.exc) if err.exc else err.get_error()

            # Detect undefined variable/function error by message content or type
            if "name" in err_msg.lower() and ("not defined" in err_msg.lower() or "undefined" in err_msg.lower()):
                # Extract variable name from error message if possible
                var_name = None
                # err.expr usually contains the offending name
                if hasattr(err, "expr") and err.expr:
                    var_name = err.expr
                elif err_msg:
                    # fallback parse variable name from string (very rough)
                    import re
                    match = re.search(r"name '(\w+)'", err_msg)
                    if match:
                        var_name = match.group(1)
                if var_name:
                    return f"Error: Undefined variable or function '{var_name}'"
                else:
                    return "Error: Undefined variable or function"
            return f"Error: {err_type} - {err_msg}"
        return result
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: Invalid expression ({str(e)})"

def show_help():
    print(
        "RSC — the simplest calculator library in Python!\n"
        "Usage:\n"
        "  rsc.assign_var('a', 10)\n"
        "  print(rsc.calculate('a * 2'))\n"
        "  print(rsc.calculate('b = 5 + 3'))  # assignment\n"
        "Supports:\n"
        "  Variables, assignments, +, -, *, /, //, %, **, ^, x (multiplication), ! (factorial)\n"
        "  Built-in math functions: sin, cos, tan, log, sqrt, factorial, etc.\n"
        "  Constants: pi, e, tau\n"
        "Examples:\n"
        "  rsc.calculate('a = 5!')  # 120\n"
        "  rsc.calculate('sin(pi / 2)')  # 1.0\n"
        "  rsc.calculate('10 x 20')  # 200\n"
        "https://github.com/Rasa8877/rs-calculator\n"
        "Contact: letperhut@gmail.com\n"
    )

__version__ = "0.3.0"
__all__ = ["assign_var", "calculate", "show_help"]
