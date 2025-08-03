# 📐 RSC (Really Simple Calculator)

RSC is the simplest calculator library in Python!  
It lets you safely evaluate complex math expressions with support for variables, assignments, factorials, and many math functions.

Version: **0.3.0** – *Now with math functions, factorials, assignments & better error handling!*

---

## 🔧 Installation

```bash
pip install rsc
````

or for a specific version:

```bash
pip install rsc==0.3.0
```

---

## 🚀 Quick Start

```python
import rsc

print(rsc.calculate("2 + 3 * (4 - 1)"))    # ➜ 11
print(rsc.calculate("5 ^ 2 + 10"))          # ➜ 35
print(rsc.calculate("sin(pi / 2)"))         # ➜ 1.0
print(rsc.calculate("5! + 10"))              # ➜ 130
```

You can also assign variables:

```python
rsc.assign_var("a", 10)
rsc.assign_var("b", 20)
rsc.assign_var("c", 10)

print(rsc.calculate("a + b - c"))            # ➜ 20
print(rsc.calculate("d = (a + b) * c"))      # ➜ 300
print(rsc.calculate("d / 2"))                 # ➜ 150.0
```

---

## ✅ Supported Features

* Operators: `+`, `-`, `*`, `x` (multiplication), `/`, `//`, `%`, `**`, `^`
* Factorial operator: `!` (e.g. `5!`)
* Parentheses for grouping
* Variables and assignments (e.g. `a = 5 + 3`)
* Built-in math functions: `sin`, `cos`, `tan`, `log`, `log10`, `sqrt`, `factorial`, etc.
* Built-in constants: `pi`, `e`, `tau`
* Safe evaluation using `asteval`
* Friendly error messages

---

## 📘 Usage Reference

```python
rsc.calculate(expression: str) -> float | int | str
```

Evaluates the expression string and returns the result or error message.

```python
rsc.assign_var(name: str, value: float | int)
```

Assigns a variable for use in expressions.

```python
rsc.show_help()
```

Prints detailed usage instructions.

---

## 🌐 Links

* [GitHub Repo](https://github.com/Rasa8877/rs-calculator-rsc)
* Contact: [letperhut@gmail.com](mailto:letperhut@gmail.com)

---

## 🧠 Author

Made with ❤️ by Rasa8877
RSC — the simplest calculator library in Python!