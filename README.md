![Build Status](https://github.com/karol-sw/FXPHelper/workflows/FXPHelper/badge.svg)

# FXPHelper
A Python module which provides some help with fixed point arithmetics.
It contains a classes to represent a single or complex numbers in Q format. Additionally it implements basic arithmetics for those classes and cooperates with numpy for matrix operations.

## Installation
In order to install the FXPHelper package open a console in root directory of this repository (where the 'setup.py' file is located) and type:
  pip install .

If you want to use this package without installation it is also possible (but not recommended). All you need to do is copy the fxphelper directory to the root directory of your project.

## Usage
In order to use the package you need to import it first:
```
  from fxphelper import FXPQNumber, FXPQComplex
```

Then you can create a representation of numbers in FXP Q format as any other object, for example:
```
  Qa = FXPQNumber(1,4,4)      # this creates a number in Q(1, 4, 4) format (signed, 4 bits integral part, 4 bits of fractional part)
  Qca = FXPQComplex(0,4,8)    # this creates a complex number in Q(0, 4, 8) format (unsigned, 4 bits integral part, 8 bits of fractional part)
```

You can set the value of created numer during object creation (with hex_value, float_value/complex_value arguments) or later with dedicated load functions, for example:
```
  # this loads the Qa with raw hex value of 0x010 (which correspond to float value of 1 for Q(1, 4, 4) format).
  Qa.load_hex(0x010)

  # this loads the Qa with 1.5 value (which correspond to raw hex value of 0x018 in Q(1, 4, 4) format).
  Qa.load_float(1.5)

  # this creates a new number and load it with raw 0x200 value (which corresponds to float value of 2)
  Qb = FXPQNumber(1, 2, 8, hex_value=0x200)

  # this loads the Qca with 1+j2 complex value (which corresponds to raw hex value of 0x200100 in Q(0, 4, 8) format - please note that re and img parts are combined together)
  Qca.load_complex(complex(1,2))
```

When a number is created you can do a simple operation on them as for any other numbers, for example:
```
  Qc = Qa+Qb
```

A numbers in FXP format can be converted with to_hex or to_float/to_complex methods. Also some basic operations (like symmetric round, scaling, etc.) can be performed.

You can find more examples in the 'examples' directory.
The FXPHelper package contains a docstring-based help - if you need additional information for any method or class you can use it by typing in python console:
```
  help(class or method name)
```
For example:
```
  help(FXPQNumber)            # this will display help for whole FXPQNumber class.
  help(FXPQNumber.__add__)    # this will display help for '+' operator overriding method in FXPQNumber class.
```

## Final note
My goal during creating of this package was not only to provide some back-end for DSP calculations but also to presents the methods of performing a various FXP operations in a clean and easy way.
I realize that in some case it is not the most-pythonic but keeping it like that allows to easily understand the principals of FXP operations and implement it in any programming or hardware description language.

