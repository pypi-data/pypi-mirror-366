import rsc

print(rsc.calculate("2+3"))             # 5
print(rsc.calculate("10x20"))           # 200
print(rsc.calculate("5!"))              # 120
print(rsc.calculate("sin(pi / 2)"))     # 1.0
print(rsc.calculate("unknown_var"))     # Error: Undefined variable or function 'unknown_var'
