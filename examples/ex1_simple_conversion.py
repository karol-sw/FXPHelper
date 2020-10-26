from fxphelper import FXPQNumber

# create a number in Q(1.2.3) format and load with hex value
a=FXPQNumber(1,2,3, hex_value=0x12)
print(a.get_format())	# print format
print(hex(a.to_hex()))		# print as hex
print(a.to_float())		# print as float
print()

# create a number in Q(1.2.31) without loading initial value
b=FXPQNumber(1,4,31)
b.load_float(-3.1234)	# load with float
print(b.get_format())	# print format
print(b)				# same as hex(b.to_hex())
print(b.to_float())		# print as float
