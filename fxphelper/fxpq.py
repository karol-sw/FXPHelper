class FXPQNumber():
    """
    Class representing a fixed point number in Q(s, m, n) format.

    Args:
        SIGN_SIZE (int) : Signed number indicator (0 - unsigned, 1 - signed).
        M_SIZE (int) : Number of bits to store integer portion of a number.
        N_SIZE (int) : Number of bits to store fractional portion of a number.
        hex_value (int, optional) : Raw value of represented number to load. Defaults to 0.
        float_value (float, optional) : Decimal value to convert (to raw value) and load. Defaults to 0.
        display_format (enum, optional) : Default display format for __str__ and __repr__ methods. Possible values: C_FXP_DISPLAY_FORMAT_HEX, C_FXP_DISPLAY_FORMAT_FLOAT, C_FXP_DISPLAY_FORMAT_FULL. Defaults to C_FXP_DISPLAY_FORMAT_HEX.

    Attributes:
        SIGN_SIZE (int) : Signed number indicator (0 - unsigned, 1 - signed).
        M_SIZE (int) : Number of bits to store integer portion of a number.
        N_SIZE (int) : Number of bits to store fractional portion of a number.
        TOTAL_SIZE (int) : Number of bits to store whole number (SIGN_SIZE + M_SIZE + N_SIZE).
        hex_value (int) : Raw value of represented number.
        sign (int) : Value of sign bit.
        display_format (enum) : Selected display format.
    """
    C_FXP_DISPLAY_FORMAT_HEX    = 0
    C_FXP_DISPLAY_FORMAT_FLOAT  = 1
    C_FXP_DISPLAY_FORMAT_FULL   = 2
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, float_value=0, display_format=C_FXP_DISPLAY_FORMAT_HEX):
        # Q(SIGN.M.N)
        if SIGN_SIZE:
            self.SIGN_SIZE = 1
        else:
            self.SIGN_SIZE = 0
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE
        self.TOTAL_SIZE=self.SIGN_SIZE + self.M_SIZE + self.N_SIZE

        self.hex_value = 0
        self.sign = 0

        if hex_value:
            self.load_hex(hex_value)
        elif float_value:
            self.load_float(float_value)

        # set default display format
        self.display_format = display_format

    def load_hex(self, h):
        """
        Load raw hex value.

        Args:
            h (int): Value to load.
        """
        _mask = (1 << self.TOTAL_SIZE)-1
        # truncate MSbits - this will also convert to unsigned hex format
        # (so python will no longer display '-' in hex print)
        self.hex_value = h & _mask

        # extract sign
        if self.SIGN_SIZE:
            self.sign = (h >> (self.M_SIZE + self.N_SIZE)) & 1
        else:
            self.sign = 0

    def load_float(self, value):
        """
        Load float value.

        Args:
            value (float): Value to load.
        """
        # convert to hex value
        _tmp = int(round(value * (1 << self.N_SIZE)))
        # load
        self.load_hex(_tmp)

    def to_hex(self):
        """
        Return a raw hex value.

        Returns:
            Raw hex value of current number.
        """
        return self.hex_value

    def to_float(self):
        """
        Convert to float.

        Returns:
            Float value of current number.
        """
        if self.sign == 1:
            _mask = (1 << self.TOTAL_SIZE) - 1
            _res = (self.hex_value ^ _mask) + 1
            _sign = -1
        else:
            _sign = 1
            _res = self.hex_value

        _res /= (1 << self.N_SIZE)
        _res *= _sign
        return _res

    def to_Q(self):
        """
        Convert to Q(s,m,n) format.

        Returns:
            Returns a tuple: (|S|, |M|, |N|), where: S-sign, M-integral part, N-fractional part)
        """
        _h = self.hex_value
        if self.SIGN_SIZE:
            _s = (_h >> (self.TOTAL_SIZE - 1) ) & 1
            _mask = ((1 << (self.N_SIZE + self.M_SIZE))-1)
            _h &= _mask      # get value without sign
            _h ^= _mask      # invert all bits
            _h += 1          # add 1 (U2 conversion)
        else:
            _s = 0

        if self.M_SIZE:
            _m = (_h >> self.N_SIZE) & ((1 << self.M_SIZE)-1)
        else:
            _m = 0

        if self.N_SIZE:
            _n = _h & ((1 << self.N_SIZE)-1)
        else:
            _n = 0

        return (_s, _m, _n)

    def get_format(self):
        """
        Get FXP Q format.

        Returns:
            Returns a tuple: (sign size, m-part size, n-part size).
        """
        return (self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)

    def _scale(self, sign_size, m_size, n_size, round=False):
        # for internal use only
        # returns a hex scaled to a given size
        _delta_n = n_size - self.N_SIZE
        _delta_m = m_size - self.M_SIZE
        if (self.SIGN_SIZE == 0 and sign_size != 0):
            _delta_s = 1
        elif (self.SIGN_SIZE != 0 and sign_size == 0):
            _delta_s = -1
        else:
            _delta_s = 0

        _hex_value = self.hex_value
        # first resize the N (friction) part
        # (operation done on whole number as rounding may impact the M part)
        if _delta_n > 0:
            # increase precision - fill right side with zeros
            _hex_value = self.hex_value << (_delta_n)
        elif _delta_n < 0:
            # decrease precision - cut right part
            if round:
                _hex_value = self.hex_value + (1 << (-_delta_n-1))
            _hex_value = (_hex_value >> -_delta_n)

        # extract _s, _n and _m values
        _n = _hex_value & ((1 << n_size) - 1)
        _m = (_hex_value >> n_size) & ((1 << self.M_SIZE) -1 )
        # self.sign cannot be used as rounding may change the sign value
        # (rounding negative value to 0)
        if sign_size:
            _s = (_hex_value >> (n_size + self.M_SIZE)) & 1
        else:
            _s = 0

        # now resize the M part
        if _delta_m > 0:
            # increase capacity - fill left side with sign
            for i in range(_delta_m):
                _m |= _s << (self.M_SIZE+i)
        elif _delta_m < 0:
            # decrease capacity - cut left side (and pray to not lost anything)
            _m &= ((1 << m_size)-1)

        # combine all together and return
        _hex_value = _n | (_m << n_size) | (_s << (n_size+m_size))
        return _hex_value

    def sym_round(self, round_factor):
        """
        Perform a symmetric round operation (used to increase or decrease number's friction precision).

        Args:
            round_factor (int): Number of bits to cut (if >0) or extend (if <0) the friction part.

        Returns:
            Returns a FXPQNumber after performing symmetric round operation.
        """
        _hex_value = self._scale(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE-round_factor, True)
        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE-round_factor, _hex_value, display_format=self.display_format)
        return _res

    def scale(self, sign_size, m_size, n_size, round=False):
        """
        Scale current number to different Q format without changing its (float) value.

        Args:
            sign_size (int): New size of the sign part.
            m_size (int): New size of the integral part.
            n_size (int): New size of the fractional part.
            round (bool, optional) : Select if rounding should be enabled if number is scaled down (false by default).

        Returns:
            Returns a FXPQNumber after performing scaling operation.
        """
        _hex_value = self._scale(sign_size, m_size, n_size, round)
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size
        self.load_hex(_hex_value)

    def resize(self, sign_size, m_size, n_size):
        """
        Cast current raw value to a different Q format.
        Resize function may be used when we want to interpret current hex as it was in different Q format
        Typical usecase: A Q(1.1.2) + B Q(1.1.2) = C Q(1.1.2) - adding with no overflow
        C = A+B             # C will be in format Q(1.2.2)
        C.resize(1,1,2)     # resize to format Q(1.1.2)

        Args:
            sign_size (int): New size of the sign part.
            m_size (int): New size of the integral part.
            n_size (int): New size of the fractional part.
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size
        self.load_hex(self.hex_value)

    # a little hack is here - by default __str__ in numpy for unknown types displays
    # a type - so we will override a type return value to get a real number value
    def __repr__(self):
        if self.display_format==self.C_FXP_DISPLAY_FORMAT_HEX:
            _disp = hex(self.hex_value)
        elif self.display_format==self.C_FXP_DISPLAY_FORMAT_FLOAT:
            _disp = self.to_float()
        else:
            _disp = "Q{:s} 0x{:x} {:f}".format(str(self.get_format()), self.to_hex(), self.to_float())

        return str(_disp)

    def __str__(self):
        if self.display_format==self.C_FXP_DISPLAY_FORMAT_HEX:
            _disp = hex(self.hex_value)
        elif self.display_format==self.C_FXP_DISPLAY_FORMAT_FLOAT:
            _disp = self.to_float()
        else:
            _disp = "Q{:s} 0x{:x} {:f}".format(str(self.get_format()), self.to_hex(), self.to_float())

        return str(_disp)

    def _convert_arg(self, y):
        # for internal purpose only
        # check argument type and convert to FXP if needed
        if isinstance(y, (int, float)):
            _y = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE, float_value=y, display_format=self.display_format)
        else:
            _y = y

        return _y

    def __add__(self, y):
        """
        Override the '+' operator.

        Args:
            y (FXPQNumber or float) : Right side value of the expression

        Returns:
            Returns self + y value in FXPQNumber format.
        """
        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format
        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))

        # calculate result
        _c = _a + _b
        # _c &= (1 << (self.M_SIZE + self.N_SIZE + self.SIGN_SIZE + 1))-1 # mask is already in load_hex - no need here
        _res = FXPQNumber(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE), _c, display_format=self.display_format)
        return _res

    __radd__ = __add__

    def __sub__(self, y):
        """
        Override the '-' operator.

        Args:
            y (FXPQNumber or float) : Right side value of the expression

        Returns:
            Returns self - y value in FXPQNumber format.
        """

        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format
        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))

        # calculate result
        _c = _a - _b
        _res = FXPQNumber(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE), _c, display_format=self.display_format)
        return _res

    def __rsub__(self, x):
        # if not FXPQNumber - convert
        _a = self._convert_arg(x)

        # for sub we need to switch arguments as a-b != b-a
        _res = _a - self
        return _res

    def __mul__(self, y):
        """
        Override the '*' operator.

        Args:
            y (FXPQNumber or float) : Right side value of the expression

        Returns:
            Returns self * y value in FXPQNumber format.
        """
        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format by multiplying MSB
        # note that we do not normalize the N part for mult (like it was for add or sub)
        _new_size = self.N_SIZE + self.M_SIZE + _y.M_SIZE + _y.N_SIZE # + max([self.SIGN_SIZE != 0, y.SIGN_SIZE])

        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), _new_size - self.N_SIZE, self.N_SIZE)
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), _new_size - _y.N_SIZE, _y.N_SIZE)

        # calculate result
        _c = _a * _b
        _res = FXPQNumber(max(self.SIGN_SIZE, _y.SIGN_SIZE), self.M_SIZE+_y.M_SIZE, self.N_SIZE+_y.N_SIZE, _c, display_format=self.display_format)
        return _res

    __rmul__ = __mul__

    def __abs__(self):
        """
        Override the 'abs' operator.

        Returns:
            Returns abs(self) value in FXPQNumber format.
        """
        # returns absolute value
        if self.sign:
            _h = ~self.hex_value + 1
        else:
            _h = self.hex_value

        _res = FXPQNumber(0, self.M_SIZE, self.N_SIZE, _h, display_format=self.display_format)
        return _res


    def __truediv__(self, y):
        """
        Override the '/' operator.

        Args:
            y (FXPQNumber or float) : Right side value of the expression

        Returns:
            Returns self / y value in FXPQNumber format.
        """
        # if not FXPQNumber - convert
        _b = self._convert_arg(y)

        # store sign value
        if _b.sign == self.sign:
            _sign = 0
        else:
            _sign = 1

        # for fxp DIV operations q=a/b instead of resizing both arguments
        # we need to resize only the dividend (a) to format matching
        # a=q*b
        # Assuming that we want result to be in the same format as dividend (before resizing):
        _a = self._scale(self.SIGN_SIZE, self.M_SIZE+_b.M_SIZE, self.N_SIZE+_b.N_SIZE)

        # store divisor size
        _divisor_size = self.M_SIZE+_b.M_SIZE + self.N_SIZE+_b.N_SIZE

        # get hex values to calculations (without sign)
        # print(hex(_a))
        # print(hex(_b.to_hex()))
        if self.sign:
            _a = ~_a + 1
            _a &= (1 << _divisor_size)-1
        _b = abs(_b).to_hex()

        # print(hex(_sign))
        # print(hex(_a))
        # print(hex(_b))
        # now we can do the calculation (for example with long division algorithm)
        _q = 0
        _acum = 0
        # print("End of iteration: S, q={:b}, _a={:b}, _acum={:b}". format(_q, _a, _acum))
        for i in range(_divisor_size):
            # shift result (_q)
            _q = _q << 1

            # select next bit from dividend (_a_bit)
            _a_bit = (_a >> (_divisor_size-i-1)) & 1

            # shift acum
            _acum = (_acum << 1) | _a_bit

            # if divisor is lower than acum - add 1 to the result and evaluate new acum value
            if (_acum >= _b):
                _q |= 1
                _acum = _acum - _b
            # print("End of iteration: {:d}, q={:b}, _a_bit={:b}, _acum={:b}". format(i, _q, _a_bit, _acum))

        # rounding - not the most elegant solution but works
        # for negative value, increase ABS value when remainder (_acum) > _b/2 (-1.5 -> -1; -1.6 -> -2)
        # for positive value, increase ABS value when remainder (_acum) >= _b/2 (1.5->2)
        if (_sign == 1 and 2*_acum > _b) or (_sign == 0 and 2*_acum >= _b):
            _q += 1

        # apply sign to the result
        if _sign:
            _q = ~_q + 1


        # pack result and return
        _res = FXPQNumber(max(self.SIGN_SIZE, y.SIGN_SIZE), self.M_SIZE, self.N_SIZE, _q, display_format=self.display_format)
        return _res

    def __rtruediv__(self, x):
        # if not FXPQNumber - convert
        _a = self._convert_arg(x)

        # for div we need to switch arguments as a/b != b/a like it was in mult or add operations
        _res = _a / self
        return _res

class FXPQComplex():
    """
    Class representing a complex fixed point number in Q(s, m, n) format.

    Args:
        SIGN_SIZE (int) : Signed number indicator (0 - unsigned, 1 - signed).
        M_SIZE (int) : Number of bits to store integer portion of a number.
        N_SIZE (int) : Number of bits to store fractional portion of a number.
        hex_value (int, optional) : Raw value of represented number to load. Assembled from imag-part (MSB) and re-part (LSB) combined together. Defaults to 0.
        complex_value (comlex, optional) : Complex value to convert (to raw value) and load. Defaults to 0.
        display_format (enum, optional) : Default display format for __str__ and __repr__ methods. Possible values: C_FXP_DISPLAY_FORMAT_HEX, C_FXP_DISPLAY_FORMAT_COMPLEX, C_FXP_DISPLAY_FORMAT_FULL. Defaults to C_FXP_DISPLAY_FORMAT_COMPLEX.

    Attributes:
        TOTAL_SIZE (int) : Number of bits to store whole number (SIGN_SIZE + M_SIZE + N_SIZE).
        qRE (FXPQNumber) : re-part of the complex number (stored in FXPQNumber format).
        qIMG (FXPQNumber) : imag-part of the complex number (stored in FXPQNumber format).
        display_format (enum) : Selected display format.
    """
    C_FXP_DISPLAY_FORMAT_HEX        = 0
    C_FXP_DISPLAY_FORMAT_COMPLEX    = 1
    C_FXP_DISPLAY_FORMAT_FULL       = 2
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, complex_value=complex(0, 0), display_format=C_FXP_DISPLAY_FORMAT_COMPLEX):
        self.TOTAL_SIZE = SIGN_SIZE + M_SIZE + N_SIZE

        self.qRE = FXPQNumber(SIGN_SIZE, M_SIZE, N_SIZE)
        self.qIMG = FXPQNumber(SIGN_SIZE, M_SIZE, N_SIZE)

        if hex_value:
            self.load_hex(hex_value)
        elif complex_value:
            self.load_complex(complex_value)

        # set default display format
        self.display_format = display_format

    def load_hex(self, h):
        """
        Extract re-part and imag-part and load raw hex values.

        Args:
            h (int): Value to load.
        """
        _mask = (1 << self.TOTAL_SIZE) - 1
        _re = h & _mask
        _img = (h >> self.TOTAL_SIZE) & _mask
        self.qRE.load_hex(_re)
        self.qIMG.load_hex(_img)

    def load_complex(self, f):
        """
        Load qRE and qIMG with given complex value.

        Args:
            value (complex): Value to load.
        """
        self.qRE.load_float(f.real)
        self.qIMG.load_float(f.imag)

    def to_hex(self):
        """
        Return a raw hex value (combined re and imag parts).

        Returns:
            Raw hex value of current number.
        """
        _tmp = 0
        _tmp |= self.qRE.to_hex()
        _tmp |= self.qIMG.to_hex() << self.TOTAL_SIZE
        return _tmp

    def to_complex(self):
        """
        Convert to complex number.

        Returns:
            Comlex value of current number.
        """
        _re = self.qRE.to_float()
        _img = self.qIMG.to_float()
        return complex(_re, _img)

    def get_format(self):
        """
        Get FXP Q format. Same Q format is used for both re-part and img-part.

        Returns:
            Returns a tuple: (sign size, m-part size, n-part size).
        """
        return self.qRE.get_format()

    def sym_round(self, round_factor):
        """
        Perform a symmetric round operation (used to increase or decrease number's friction precision).
        Operation is performed separately on re-part and imag-part.

        Args:
            round_factor (int): Number of bits to cut (if >0) or extend (if <0) the friction part.

        Returns:
            Returns a FXPQComplex after performing symmetric round operation.
        """
        _re = self.qRE.sym_round(round_factor)
        _img = self.qIMG.sym_round(round_factor)
        _hex_value = (_img.to_hex() << _img.TOTAL_SIZE) | _re.to_hex()
        return FXPQComplex(_re.SIGN_SIZE, _re.M_SIZE, _re.N_SIZE, _hex_value, display_format=self.display_format)

    def scale(self, sign_size, m_size, n_size, round=False):
        """
        Scale current number to different Q format without changing its (complex) value.

        Args:
            sign_size (int): New size of the sign part.
            m_size (int): New size of the integral part.
            n_size (int): New size of the fractional part.
            round (bool, optional) : Select if rounding should be enabled if number is scaled down (false by default).

        Returns:
            Returns a FXPQComplex after performing scaling operation.
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size

        self.qRE.scale(sign_size, m_size, n_size, round)
        self.qIMG.scale(sign_size, m_size, n_size, round)

    def resize(self, sign_size, m_size, n_size):
        """
        Cast current raw value to a different Q format.

        Args:
            sign_size (int): New size of the sign part.
            m_size (int): New size of the integral part.
            n_size (int): New size of the fractional part.
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size

        self.qRE.resize(sign_size, m_size, n_size)
        self.qIMG.resize(sign_size, m_size, n_size)

    def conjugate(self):
        """
        Calculate conjugate value.

        Returns:
            Returns (self.qRE - self.qIMG) in FXPQComplex format.
        """
        _res_RE = self.qRE
        _res_IMG = 0-self.qIMG
        _res_IMG.resize(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE) # resize as sub changed format
        _hex_value = (_res_IMG.to_hex() << _res_RE.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value, display_format=self.display_format)

    def __repr__(self):
        if self.display_format==self.C_FXP_DISPLAY_FORMAT_HEX:
            _disp = "0x{:x} +j0x{:x}".format(self.qRE.to_hex(), self.qIMG.to_hex())
        elif self.display_format==self.C_FXP_DISPLAY_FORMAT_COMPLEX:
            _disp = str(self.to_complex())
        else:
            _disp = "Q{:s} (0x{:x} +j0x{:x}) {:s}".format(str(self.get_format()), self.qRE.to_hex(), self.qIMG.to_hex(), str(self.to_complex()))

        return str(_disp)


    def __str__(self):
        if self.display_format==self.C_FXP_DISPLAY_FORMAT_HEX:
            _disp = "0x{:x} +j0x{:x}".format(self.qRE.to_hex(), self.qIMG.to_hex())
        elif self.display_format==self.C_FXP_DISPLAY_FORMAT_COMPLEX:
            _disp = str(self.to_complex())
        else:
            _disp = "Q{:s} (0x{:x} +j0x{:x}) {:s}".format(str(self.get_format()), self.qRE.to_hex(), self.qIMG.to_hex(), str(self.to_complex()))

        return str(_disp)

    def _convert_arg(self, y):
        # for internal purpose only
        # check argument type and convert to FXP if needed
        if isinstance(y, (complex)):
            _y = FXPQComplex (self.qRE.SIGN_SIZE, self.qRE.M_SIZE, self.qRE.N_SIZE, complex_value=y, display_format=self.display_format)
        elif isinstance(y, (int, float)):
            _y = FXPQComplex (self.qRE.SIGN_SIZE, self.qRE.M_SIZE, self.qRE.N_SIZE, complex_value=complex(y, 0), display_format=self.display_format)
        else:
            _y = y

        return _y

    def __add__(self, y):
        """
        Override the '+' operator.

        Args:
            y (FXPQComplex or float) : Right side value of the expression

        Returns:
            Returns (self.qRE + y.qRE) + j(self.qIMG + y.qIMG) value in FXPQComplex format.
        """
        _y = self._convert_arg(y)

        _res_RE = self.qRE + _y.qRE
        _res_IMG = self.qIMG + _y.qIMG
        _hex_value = (_res_IMG.to_hex() << _res_IMG.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value, display_format=self.display_format)

    __radd__ = __add__

    def __sub__(self, y):
        """
        Override the '-' operator.

        Args:
            y (FXPQComplex or float) : Right side value of the expression

        Returns:
            Returns (self.qRE - y.qRE) + j(self.qIMG - y.qIMG) value in FXPQComplex format.
        """
        _y = self._convert_arg(y)

        _res_RE = self.qRE - _y.qRE
        _res_IMG = self.qIMG - _y.qIMG
        _hex_value = (_res_IMG.to_hex() << _res_IMG.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value, display_format=self.display_format)

    def __rsub__(self, x):
        # if not FXPQNumber - convert
        _a = self._convert_arg(x)

        # for sub we need to switch arguments as a-b != b-a
        _res = _a - self
        return _res

    def __mul__(self, y):
        """
        Override the '*' operator.

        Args:
            y (FXPQComplex or float) : Right side value of the expression

        Returns:
            Returns (self.qRE*y.qRE - self.qIMG*y.qIMG) + j(self.qRE*y.qIMG + self.qIMG*y.qRE) value in FXPQComplex format.
        """
        _y = self._convert_arg(y)

        # calculate RE and IMG part
        _res_RE = self.qRE*_y.qRE - self.qIMG*_y.qIMG
        _res_IMG = self.qRE*_y.qIMG + self.qIMG*_y.qRE

        # resize is needed as +/- operation increased m_size 1 bit too much
        _res_RE.resize(_res_RE.SIGN_SIZE, _res_RE.M_SIZE-1, _res_RE.N_SIZE)
        _res_IMG.resize(_res_IMG.SIGN_SIZE, _res_IMG.M_SIZE-1, _res_IMG.N_SIZE)

        # pack and return
        _hex_value = (_res_IMG.to_hex() << _res_RE.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value, display_format=self.display_format)

    __rmul__ = __mul__


    def __truediv__(self, y):
        """
        Override the '/' operator.

        Args:
            y (FXPQComplex or float) : Right side value of the expression

        Returns:
            Returns (self / y) value in FXPQComplex format.
        """
        # (a+bi) / (c+di) = [(a+bi)*(c-di)] / [(c+di)-(c-di)] = [(a+bi)*(c-di)]/(c*c + d*d)
        _y = self._convert_arg(y)

        # calculate _div = (c*c + d*d)
        _div = _y.qRE*_y.qRE + _y.qIMG*_y.qIMG

        # calculate RE and IMG part (step 1: x*_y_conj)
        _res_RE = self.qRE*_y.qRE + self.qIMG*_y.qIMG
        _res_IMG = self.qIMG*_y.qRE - self.qRE*_y.qIMG

        # resize is needed as +/- operation increased m_size 1 bit too much
        _res_RE.resize(_res_RE.SIGN_SIZE, _res_RE.M_SIZE-1, _res_RE.N_SIZE)
        _res_IMG.resize(_res_IMG.SIGN_SIZE, _res_IMG.M_SIZE-1, _res_IMG.N_SIZE)

        # calculate RE and IMG part (step 2: (x*_y_conj)/_div )
        _res_RE /= _div
        _res_IMG /= _div

        # pack and return
        _hex_value = (_res_IMG.to_hex() << _res_RE.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value, display_format=self.display_format)

    def __rtruediv__(self, x):
        # if not FXPQNumber - convert
        _a = self._convert_arg(x)

        # for div we need to switch arguments as a/b != b/a
        _res = _a / self
        return _res
