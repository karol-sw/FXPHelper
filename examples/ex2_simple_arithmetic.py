from fxphelper import FXPQNumber, FXPQComplex

# simple numbers
Qa = FXPQNumber(1,4,4)
Qb = FXPQNumber(1,4,4)

# complex numbers
Qca = FXPQComplex(1,4,11)
Qcb = FXPQComplex(1,4,11)

a = -15.1258
b = 1.25

ca = complex(-0.2, -0.8)
cb = complex(10.5, -0.25)

Qa.load_float(a)
Qb.load_float(b)

Qca.load_complex(ca)
Qcb.load_complex(cb)

print("Add results")
y = a+b
Qy = Qa+Qb
print(y)
print(Qy.to_float())
cy = ca+cb
Qcy = Qca+Qcb
print(cy)
print(Qcy.to_complex())


print("Sub results")
y = a-b
Qy = Qa-Qb
print(y)
print(Qy.to_float())
cy = ca-cb
Qcy = Qca-Qcb
print(cy)
print(Qcy.to_complex())

print("Mult results")
y = a*b
Qy = Qa*Qb
print(y)
print(Qy.to_float())
cy = ca*cb
Qcy = Qca*Qcb
print(cy)
print(Qcy.to_complex())

