class FXPQNumber():
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, float_value=0):
        # Q(SIGN.M.N)
        # TODO: add configuration describing default display method (hex/float)
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

    def load_hex(self, h):
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
        # convert to hex value
        _tmp = int(round(value * (1 << self.N_SIZE)))
        self.load_hex(_tmp)

    def to_hex(self):
        return self.hex_value

    def to_float(self):
        # _res = self.sign*(self.m + self.n / (1 << self.N_SIZE))
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
        # returns (|S|, |M|, |N|)
        if self.SIGN_SIZE:
            _s = (self.hex_value >> (self.TOTAL_SIZE - 1) ) & 1
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

        # extract _n and _m values
        _n = _hex_value & ((1 << n_size) - 1)
        _m = (_hex_value >> n_size) & ((1 << self.M_SIZE) -1 )

        # now resize the M part
        if _delta_m > 0:
            # increase capacity - fill left side with sign
            for i in range(_delta_m):
                _m |= self.sign << (self.M_SIZE+i)
        elif _delta_m < 0:
            # decrease capacity - cut left side (and pray to not lost anything)
            _m &= ((1 << m_size)-1)

        # evaluate the sign part
        if sign_size:
            _s = self.sign
        else:
            _s = 0

        # combine all together and return
        _hex_value = _n | (_m << n_size) | (_s << (n_size+m_size))
        return _hex_value

    def sym_round(self, round_factor):
        """
        Symetric round operation is used to increase or decrease number's friction precision
        """
        _hex_value = self._scale(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE-round_factor, True)
        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE-round_factor, _hex_value)
        return _res

    def scale(self, sign_size, m_size, n_size, round=False):
        """
        Scale current number to different Q format without changing its (float) value.
        """
        _hex_value = self._scale(sign_size, m_size, n_size, round)
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size
        self.load_hex(_hex_value)

    def resize(self, sign_size, m_size, n_size):
        """
        Resize function may be used when we want to interpret current hex as it was in different Q format
        Typical usecase: A Q(1.1.2) + B Q(1.1.2) = C Q(1.1.2) - adding with no overflow
        C = A+B             # C will be in format Q(1.2.2)
        C.resize(1,1,2)     # resize to format Q(1.1.2)
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size
        self.load_hex(self.hex_value)

    # a little hack is here - by default __str__ in numpy for unknown types displays
    # a type - so we will override a type return value to get a real number value
    def __repr__(self):
        return str(hex(self.hex_value))

    def __str__(self):
        return str(hex(self.hex_value))

    def _convert_arg(self, y):
        # for internal purpose only
        # check argument type and convert to FXP if needed
        if isinstance(y, (int, float)):
            _y = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE, float_value=y)
        else:
            _y = y

        return _y

    def __add__(self, y):
        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format
        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))

        # calculate result
        _c = _a + _b
        # _c &= (1 << (self.M_SIZE + self.N_SIZE + self.SIGN_SIZE + 1))-1 # mask is already in load_hex - no need here
        _res = FXPQNumber(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE), _c)
        return _res

    __radd__ = __add__

    def __sub__(self, y):
        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format
        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE))

        # calculate result
        _c = _a - _b
        _res = FXPQNumber(max(self.SIGN_SIZE, _y.SIGN_SIZE), max(self.M_SIZE, _y.M_SIZE)+1, max(self.N_SIZE, _y.N_SIZE), _c)
        return _res

    __rsub__ = __sub__

    def __mul__(self, y):
        # if not FXPQNumber - convert
        _y = self._convert_arg(y)

        # resize arguments to target format by multiplying MSB
        # note that we not normalize the N part for mult (like it was for add or sub)
        _new_size = self.N_SIZE + self.M_SIZE + y.M_SIZE + y.N_SIZE # + max([self.SIGN_SIZE != 0, y.SIGN_SIZE])

        _a = self._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), _new_size - self.N_SIZE, self.N_SIZE)
        _b = _y._scale(max(self.SIGN_SIZE, _y.SIGN_SIZE), _new_size - _y.N_SIZE, _y.N_SIZE)

        # calculate result
        _c = _a * _b
        _res = FXPQNumber(max(self.SIGN_SIZE, y.SIGN_SIZE), self.M_SIZE+y.M_SIZE, self.N_SIZE+y.N_SIZE, _c)
        return _res

    __rmul__ = __mul__

# a complex number in Q format
class FXPQComplex():
    # re[Q(SIGN.M.N)], img[Q(SIGN.M.N)]
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, complex_value=complex(0, 0)):
        self.TOTAL_SIZE = SIGN_SIZE + M_SIZE + N_SIZE

        self.qRE = FXPQNumber(SIGN_SIZE, M_SIZE, N_SIZE)
        self.qIMG = FXPQNumber(SIGN_SIZE, M_SIZE, N_SIZE)

        if hex_value:
            self.load_hex(hex_value)
        elif complex_value:
            self.load_complex(complex_value)

    def load_hex(self, h):
        _mask = (1 << self.TOTAL_SIZE) - 1
        _re = h & _mask
        _img = (h >> self.TOTAL_SIZE) & _mask
        self.qRE.load_hex(_re)
        self.qIMG.load_hex(_img)

    def load_complex(self, f):
        self.qRE.load_float(f.real)
        self.qIMG.load_float(f.imag)

    def to_hex(self):
        _tmp = 0
        _tmp |= self.qRE.to_hex()
        _tmp |= self.qIMG.to_hex() << self.TOTAL_SIZE
        return _tmp

    def to_complex(self):
        _re = self.qRE.to_float()
        _img = self.qIMG.to_float()
        return complex(_re, _img)

    def get_format(self):
        return self.qRE.get_format()

    def sym_round(self, round_factor):
        """
        Symetric round operation is used to increase or decrease number's friction precision
        """
        _re = self.qRE.sym_round(round_factor)
        _img = self.qIMG.sym_round(round_factor)
        _hex_value = (_img.to_hex() << _img.TOTAL_SIZE) | _re.to_hex()
        return FXPQComplex(_re.SIGN_SIZE, _re.M_SIZE, _re.N_SIZE, _hex_value)

    def scale(self, sign_size, m_size, n_size, round=False):
        """
        Scale current number to different Q format without changing its (float) value.
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size

        self.qRE.scale(sign_size, m_size, n_size, round)
        self.qIMG.scale(sign_size, m_size, n_size, round)

    def resize(self, sign_size, m_size, n_size):
        """
        Resize function may be used when we want to interpret current hex as it was in different Q format
        Typical usecase: A Q(1.1.2) + B Q(1.1.2) = C Q(1.1.2) - adding with no overflow
        C = A+B             # C will be in format Q(1.2.2)
        C.resize(1,1,2)     # resize to format Q(1.1.2)
        """
        self.SIGN_SIZE = sign_size
        self.M_SIZE=m_size
        self.N_SIZE=n_size
        self.TOTAL_SIZE = sign_size + m_size + n_size

        self.qRE.resize(sign_size, m_size, n_size)
        self.qIMG.resize(sign_size, m_size, n_size)

    def __repr__(self):
        # return "{:x} +j{:x}".format(self.qRE.to_hex(), self.qIMG.to_hex())
        return str(complex(self.qRE.to_float(), self.qIMG.to_float()))

    def __str__(self):
        return str(complex(self.qRE.to_float(), self.qIMG.to_float()))

    def _convert_arg(self, y):
        # for internal purpose only
        # check argument type and convert to FXP if needed
        if isinstance(y, (complex)):
            _y = FXPQComplex (self.qRE.SIGN_SIZE, self.qRE.M_SIZE, self.qRE.N_SIZE, complex_value=y)
        elif isinstance(y, (int, float)):
            _y = FXPQComplex (self.qRE.SIGN_SIZE, self.qRE.M_SIZE, self.qRE.N_SIZE, complex_value=complex(y, 0))
        else:
            _y = y
            print("y")

        return _y

    def __add__(self, y):
        _y = self._convert_arg(y)

        _res_RE = self.qRE + _y.qRE
        _res_IMG = self.qIMG + _y.qIMG
        _hex_value = (_res_IMG.to_hex() << _res_IMG.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value)

    __radd__ = __add__

    def __sub__(self, y):
        _y = self._convert_arg(y)

        _res_RE = self.qRE - _y.qRE
        _res_IMG = self.qIMG - _y.qIMG
        _hex_value = (_res_IMG.to_hex() << _res_IMG.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value)

    __rsub__ = __sub__

    def __mul__(self, y):
        _y = self._convert_arg(y)

        # calculate RE and IMG part
        _res_RE = self.qRE*_y.qRE - self.qIMG*_y.qIMG
        _res_IMG = self.qRE*_y.qIMG + self.qIMG*_y.qRE

        # resize is needed as +/- operation increased m_size 1 bit too much
        _res_RE.resize(_res_RE.SIGN_SIZE, _res_RE.M_SIZE-1, _res_RE.N_SIZE)
        _res_IMG.resize(_res_IMG.SIGN_SIZE, _res_IMG.M_SIZE-1, _res_IMG.N_SIZE)

        # pack and return
        _hex_value = (_res_IMG.to_hex() << _res_RE.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value)

    __rmul__ = __mul__
