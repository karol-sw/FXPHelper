from fxphelper import FXPQNumber

Qa = FXPQNumber(1,4,31)
Qb = FXPQNumber(1,4,31)

a = 0.21
b = -0.2

Qa.load_float(a)
Qb.load_float(b)

y = a+b
Qy = Qa+Qb

#y = a*b
#Qy = Qa*Qb

print(y)
print(Qy.to_float())
