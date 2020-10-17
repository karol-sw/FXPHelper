import unittest
from fxphelper import *

C_TEST_PRECISION = 5

class TestConversion(unittest.TestCase):
    # ---------------- unsigned int --------------------
    def test_arith_unsigned_int_sum(self):
        x = 3;
        y = 8;
        qx = FXPQNumber(0,5,0, float_value = x);
        qy = FXPQNumber(0,5,0, float_value = y);
        z = x + y
        qz = qx + qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_int_sub(self):
        x = 3;
        y = 8;
        qx = FXPQNumber(0,5,0, float_value = x);
        qy = FXPQNumber(0,5,0, float_value = y);
        z = x - y + (2**6)  # result in Q(0.6.0), +overflow
        qz = qx - qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_int_mult(self):
        x = 3;
        y = 8;
        qx = FXPQNumber(0,5,0, float_value = x);
        qy = FXPQNumber(0,5,0, float_value = y);
        z = x * y
        qz = qx * qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_int_div(self):
        x = 8;
        y = 2;
        qx = FXPQNumber(0,5,0, float_value = x);
        qy = FXPQNumber(0,5,0, float_value = y);
        z = x / y
        qz = qx / qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    # ---------------- unsigned float --------------------
    def test_arith_unsigned_float_sum(self):
        x = 3.2;
        y = 8.1;
        qx = FXPQNumber(0,5,22, float_value = x);
        qy = FXPQNumber(0,5,22, float_value = y);
        z = x + y
        qz = qx + qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_float_sub(self):
        x = 8.1;
        y = 3.2;
        qx = FXPQNumber(0,5,22, float_value = x);
        qy = FXPQNumber(0,5,22, float_value = y);
        z = x - y
        qz = qx - qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_float_mult(self):
        x = 3.2;
        y = 8.1;
        qx = FXPQNumber(0,5,22, float_value = x);
        qy = FXPQNumber(0,5,22, float_value = y);
        z = x * y
        qz = qx * qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_unsigned_float_div(self):
        x = 8.1;
        y = 2.2;
        qx = FXPQNumber(0,5,22, float_value = x);
        qy = FXPQNumber(0,5,22, float_value = y);
        z = x / y
        qz = qx / qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    # ---------------- signed int --------------------
    def test_arith_signed_int_sum(self):
        x = -3;
        y = -8;
        qx = FXPQNumber(1,5,0, float_value = x);
        qy = FXPQNumber(1,5,0, float_value = y);
        z = x + y
        qz = qx + qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_int_sub(self):
        x = -3;
        y = -8;
        qx = FXPQNumber(1,5,0, float_value = x);
        qy = FXPQNumber(1,5,0, float_value = y);
        z = x - y
        qz = qx - qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_int_mult(self):
        x = -3;
        y = -8;
        qx = FXPQNumber(1,5,0, float_value = x);
        qy = FXPQNumber(1,5,0, float_value = y);
        z = x * y
        qz = qx * qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_int_div(self):
        x = -8;
        y = -2;
        qx = FXPQNumber(1,5,0, float_value = x);
        qy = FXPQNumber(1,5,0, float_value = y);
        z = x / y
        qz = qx / qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    # ---------------- signed float --------------------
    def test_arith_signed_float_sum(self):
        x = -3.2;
        y = -8.1;
        qx = FXPQNumber(1,5,22, float_value = x);
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x + y
        qz = qx + qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_sub(self):
        x = -8.1;
        y = -3.2;
        qx = FXPQNumber(1,5,22, float_value = x);
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x - y
        qz = qx - qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_mult(self):
        x = -3.2;
        y = -8.1;
        qx = FXPQNumber(1,5,22, float_value = x);
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x * y
        qz = qx * qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_div(self):
        x = -8.1;
        y = -2.2;
        qx = FXPQNumber(1,5,22, float_value = x);
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x / y
        qz = qx / qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)


    # ------------- signed float by constant ----------------
    def test_arith_signed_float_sum_const(self):
        x = -3.2;
        y =  8.1;
        qx = FXPQNumber(1,5,22, float_value = x);
        z = x + y
        qz = qx + y
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_sub_const(self):
        x = 8.1;
        y = -3.2;
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x - y
        qz = x - qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_mult_const(self):
        x = -3.2;
        y = 8.1;
        qx = FXPQNumber(1,5,22, float_value = x);
        z = x * y
        qz = qx * y
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)

    def test_arith_signed_float_div_const(self):
        x = 8.1;
        y = -2.2;
        qy = FXPQNumber(1,5,22, float_value = y);
        z = x / y
        qz = x / qy
        self.assertAlmostEqual(qz.to_float(), z, C_TEST_PRECISION)


    # ---------------- signed float (complex) --------------------
    def test_arith_cpl_signed_float_sum(self):
        x = complex(-1.2, 2.0);
        y = complex(0.1, -8.1);
        qx = FXPQComplex(1,5,22, complex_value = x);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x + y
        qz = qx + qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_sub(self):
        x = complex(-8.1, 2.25);
        y = complex(-3.2, -3.0);
        qx = FXPQComplex(1,5,22, complex_value = x);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x - y
        qz = qx - qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_mult(self):
        x = complex(-1.7, 2.3);
        y = complex(-0.1, 2.4) ;
        qx = FXPQComplex(1,5,22, complex_value = x);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x * y
        qz = qx * qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_div(self):
        x = complex(-1.1, -4.1);
        y = complex(-4.2, 2.1);
        qx = FXPQComplex(1,5,22, complex_value = x);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x / y
        qz = qx / qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    # ---------- signed float by constant (complex)-------------
    def test_arith_cpl_signed_float_sum_const(self):
        x = complex(-1.2, 2.0);
        y = complex(0.1, -8.1);
        qx = FXPQComplex(1,5,22, complex_value = x);
        z = x + y
        qz = qx + y
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_sub_const(self):
        x = -8.1;
        y = complex(-3.2, -3.0);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x - y
        qz = x - qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_mult_const(self):
        x = complex(-1.7, 2.3);
        y = complex(0, 2.4) ;
        qx = FXPQComplex(1,5,22, complex_value = x);
        z = x * y
        qz = qx * y
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

    def test_arith_cpl_signed_float_div_const(self):
        x = 1;
        y = complex(-2.2, 2.1);
        qy = FXPQComplex(1,5,22, complex_value = y);
        z = x / y
        qz = x / qy
        self.assertAlmostEqual(qz.to_complex(), z, C_TEST_PRECISION)

if __name__ == '__main__':
    unittest.main()
