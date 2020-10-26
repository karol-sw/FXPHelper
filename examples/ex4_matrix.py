import numpy as np
from fxphelper import FXPQNumber, FXPQComplex

# create some test arrays
a = [i/8 for i in range(8)]
b = [-i/4 for i in range(8)]
arr_a = np.array(a).reshape(2, 4)
arr_b = np.array(b).reshape(2, 4)
arr_c = np.array(b).reshape(4, 2)	# same values as b but different format

Qa = [FXPQNumber(1,8,16, float_value=i, display_format=FXPQNumber.C_FXP_DISPLAY_FORMAT_FLOAT) for i in a]
Qb = [FXPQNumber(1,8,16, float_value=i, display_format=FXPQNumber.C_FXP_DISPLAY_FORMAT_FLOAT) for i in b]
arr_Qa = np.array(Qa).reshape(2, 4)
arr_Qb = np.array(Qb).reshape(2, 4)
arr_Qc = np.array(Qb).reshape(4, 2)

print("\nInput arrays:")
print("arr_a:\n", arr_a)
print("arr_b:\n", arr_b)
print("arr_c:\n", arr_c)

# sum arrays
print("\nSum arrays arr_y = (arr_a + arr_b):")
arr_y = arr_a + arr_b
arr_Qy = arr_Qa + arr_Qb
print("Floating point arr_y:\n", arr_y)
print("Fixed point arr_y:\n", arr_Qy)

# sub arrays
print("\nSubtract arrays arr_y = (arr_a - arr_b):")
arr_y = arr_a - arr_b
arr_Qy = arr_Qa - arr_Qb
print("Floating point arr_y:\n", arr_y)
print("Fixed point arr_y:\n", arr_Qy)

# matrix-multiply (dot) arrays
print("\n'Dot' arrays arr_y = (arr_a.arr_c):")
arr_y = arr_a.dot(arr_c)
arr_Qy = arr_Qa.dot(arr_Qc)
print("Floating point arr_y:\n", arr_y)
print("Fixed point arr_y:\n", arr_Qy)

# transpose matrix
print("\nTranspose arr_y = (arr_a)^T:")
arr_y = arr_a.T
arr_Qy = arr_Qa.T
print("Floating point arr_y:\n", arr_y)
print("Fixed point arr_y:\n", arr_Qy)
