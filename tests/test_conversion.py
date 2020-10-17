import unittest
from fxphelper import *

C_TEST_PRECISION = 5

class TestConversion(unittest.TestCase):
    def test_conv_unsigned_int(self):
        x = 3
        y = FXPQNumber(0,5,0, float_value = x)
        self.assertAlmostEqual(y.to_float(), x, C_TEST_PRECISION)


    def test_conv_signed_int(self):
        x = -3
        y = FXPQNumber(1,5,0, float_value = x)
        self.assertAlmostEqual(y.to_float(), x, C_TEST_PRECISION)

    def test_conv_unsigned_float(self):
        x = 3.2
        y = FXPQNumber(0,4,17, float_value = x)
        self.assertAlmostEqual(y.to_float(), x, C_TEST_PRECISION)


    def test_conv_signed_float(self):
        x = -3.2
        y = FXPQNumber(1,4,17, float_value = x)
        self.assertAlmostEqual(y.to_float(), x, C_TEST_PRECISION)


    def test_conv_cpl_signed_float(self):
        x = complex(-3.2, 1.7)
        y = FXPQComplex(1,4,17, complex_value = x)
        self.assertAlmostEqual(y.to_complex(), x, C_TEST_PRECISION)


if __name__ == '__main__':
    unittest.main()
