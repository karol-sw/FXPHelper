from fxphelper import FXPQNumber

Qa = FXPQNumber(1,4,4)
Qb = FXPQNumber(1,4,4)

a = -15.1258
b = 1.25

Qa.load_float(a)
Qb.load_float(b)

print("Add results")
y = a+b
Qy = Qa+Qb
print(y)
print(Qy.to_float())

print("Sub results")
y = a-b
Qy = Qa-Qb
print(y)
print(Qy.to_float())

print("Mult results")
y = a*b
Qy = Qa*Qb
print(y)
print(Qy.to_float())
