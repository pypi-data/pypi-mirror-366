from rsc import calculate, assign_var, show_help

def repl():
    print("RSC Interactive Calculator REPL")
    print("Type 'help' for usage, 'exit' or Ctrl+C to quit.")
    while True:
        try:
            expr = input(">>> ").strip()
            if expr.lower() in ("exit", "quit"):
                print("Bye!")
                break
            if expr.lower() == "help":
                show_help()
                continue
            if "=" in expr:
                # Detect assignment to update symbol table immediately
                result = calculate(expr)
                if not isinstance(result, str) or not result.startswith("Error"):
                    print(f"Assigned: {expr}")
                else:
                    print(result)
            else:
                result = calculate(expr)
                print(result)
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except EOFError:
            print("\nBye!")
            break

if __name__ == "__main__":
    repl()
