from fxphelper import FXPQNumber, FXPQComplex

# simple numbers
Qa = FXPQNumber(1,4,4)
Qb = FXPQNumber(1,4,4)

# complex numbers
Qca = FXPQComplex(1,4,11)
Qcb = FXPQComplex(1,4,11)

# test values
a = -15.1258
b = 1.25
ca = complex(-0.2, -0.8)
cb = complex(10.5, -0.25)

# load test values into FXP structures
Qa.load_float(a)
Qb.load_float(b)

Qca.load_complex(ca)
Qcb.load_complex(cb)

print("\nInput values:")
print("a: ", a)
print("b: ", b)

print("ca: ", ca)
print("cb: ", cb)

# do the arithmetics
# ------------------------------------
print("\nAdd results (simple):")
y = a+b
Qy = Qa+Qb
print("Floating point result: ", y)
print("Fixed point result:    ", Qy.to_float())

print("\nAdd results (complex):")
cy = ca+cb
Qcy = Qca+Qcb
print("Floating point result: ", cy)
print("Fixed point result:    ", Qcy.to_complex())


# ------------------------------------
print("\nSub results (simple):")
y = a-b
Qy = Qa-Qb
print("Floating point result: ", y)
print("Fixed point result:    ", Qy.to_float())

print("\nSub results (complex):")
cy = ca-cb
Qcy = Qca-Qcb
print("Floating point result: ", cy)
print("Fixed point result:    ", Qcy.to_complex())

# ------------------------------------
print("\nMult results (simple):")
y = a*b
Qy = Qa*Qb
print("Floating point result: ", y)
print("Fixed point result:    ", Qy.to_float())

print("\nMult results (complex):")
cy = ca*cb
Qcy = Qca*Qcb
print("Floating point result: ", cy)
print("Fixed point result:    ", Qcy.to_complex())

# ------------------------------------
print("\nDivide results (simple)")
y = a/b
Qy = Qa/Qb
print("Floating point result: ", y)
print("Fixed point result:    ", Qy.to_float())

print("\nDivide results (complex)")
cy = ca/cb
Qcy = Qca/Qcb
print("Floating point result: ", cy)
print("Fixed point result:    ", Qcy.to_complex())

# ------------------------------------
print("\nConjugate a")
cc = ca.conjugate()
Qcc = Qca.conjugate()
print("Floating point result: ", cc)
print("Fixed point result:    ", Qcc.to_complex())
