from fxphelper import FXPQNumber, FXPQComplex

print("Simple number")
Q = FXPQNumber(1,4,4, float_value=-5.25)
print(Q.get_format(), Q, Q.to_float())

print("\nIncrease friction precision")
Q.scale(1,4,8)
print(Q.get_format(), Q, Q.to_float())

print("\nIncrease M")
Q.scale(1,8,8)
print(Q.get_format(), Q, Q.to_float())

print("\nDecrase friction precision")
Q.scale(1,8,2)
print(Q.get_format(), Q, Q.to_float())

print("\nDecrase M")
Q.scale(1,3,2)
print(Q.get_format(), Q, Q.to_float())

print("\nTrue rounding (>>1)")
Qr = Q.sym_round(1)
print(Qr.get_format(), Qr, Qr.to_float())
# or (if we want to change number directly)
Q.scale(0,3,1, True)

print("\nThrown away sign")
Q.scale(0,3,1)
print(Q.get_format(), Q, Q.to_float())