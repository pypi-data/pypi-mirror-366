# 📐 RSC (Really Simple Calculator)

RSC is the simplest calculator library in Python!  
It lets you evaluate complex math expressions **safely**, with support for variables and all basic math operators.

Version: **0.2.4** – *Fixed the bugs*

---

## 🔧 Installation

```bash
pip install rsc
```

or

```bash
pip install rsc==0.2.4
```

---

## 🚀 Quick Start

```python
import rsc

print(rsc.calculate("2 + 3 * (4 - 1)"))  # ➜ 11
print(rsc.calculate("5 ^ 2 + 10"))      # ➜ 35
```

You can also assign variables:

```python
rsc.assign_var("a", 10)
rsc.assign_var("b", 20)
rsc.assign_var("c", 10)

print(rsc.calculate("a + b - c"))     # ➜ 20
print(rsc.calculate("(a + b) - c"))   # ➜ 20
```

---

## ✅ Supported Features

* Operators: `+`, `-`, `*`, `x`, `/`, `//`, `%`, `**`, `^`
* Parentheses for grouping
* Variables using `assign_var(name, value)`
* Safe evaluation (using `asteval`)
* Simple API

---

## 📘 Usage Reference

```python
rsc.calculate(expression: str) -> float | str
```

```python
rsc.assign_var(name: str, value: float | int)
```

```python
rsc.show_help()  # Prints usage instructions
```

---

## 🌐 Links

* [GitHub Repo](https://github.com/Rasa8877/rs-calculator)
* Contact: [letperhut@gmail.com](mailto:letperhut@gmail.com)

---

## 🧠 Author

Made with ❤️ by Rasa8877  
RSC — the simplest calculator library in Python!
