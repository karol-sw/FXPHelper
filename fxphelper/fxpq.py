class FXPQNumber():
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, float_value=0):
        # Q(SIGN.M.N)
        # TODO: add configuration describing default display method (hex/float)
        self.SIGN_SIZE = SIGN_SIZE
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE
        self.TOTAL_SIZE=SIGN_SIZE + M_SIZE + N_SIZE

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

    # TODO: add function to_Q which returns [S, M, N]
    # if _sign:
    #     _sign_mask = ((1 << (self.N_SIZE + self.M_SIZE))-1)
    #     h &= _sign_mask     # get value without sign
    #     h ^= _sign_mask     # invert all bits
    #     h += 1              # add 1 (U2 conversion)
    #     self.sign = -1
    # else:
    #     self.sign = 1
    #
    # if self.M_SIZE:
    #     self.m = (h >> self.N_SIZE) & ((1 << self.M_SIZE)-1)
    # else:
    #     self.m = 0
    #
    # if self.N_SIZE:
    #     self.n = h & ((1 << self.N_SIZE)-1)
    # else:
    #     self.n = 0


    def sym_round(self, round_factor):
        """
        Symetric round operation is used to increase or decrease number's friction precision
        """
        # TODO: check if _scale can be used
        if round_factor < 0:
            _hex_value = self.hex_value << (-round_factor)
        elif round_factor > 0:
            _hex_value = self.hex_value + (1 << (round_factor-1))
            _hex_value = (_hex_value >> round_factor)
        else:
            _hex_value = self.hex_value

        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE-round_factor, _hex_value)
        return _res

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

    # def _scale(self, sign_size, m_size, n_size):
    #     # returns a hex scaled to given size
    #     # TODO
    #     pass
    #
    # def scale(self, sign_size, m_size, n_size):
    #     """
    #     Scale current number to different Q format without changing its (float) value.
    #     """
    #     _hex_value = _scale(self.hex_value, sign_size, m_size, n_size)
    #     self.SIGN_SIZE = sign_size
    #     self.M_SIZE=m_size
    #     self.N_SIZE=n_size
    #     self.TOTAL_SIZE = sign_size + m_size + n_size
    #     self.load_hex(_hex_value)

    # a little hack is here - by default __str__ in numpy for unknown types displays
    # a type - so we will override a type return value to get a real number value
    def __repr__(self):
        return str(hex(self.hex_value))

    def __str__(self):
        return str(hex(self.hex_value))

    def __add__(self, y):
        # TODO: add detecting non-FXP types for all functions (to allow operations with constants)
        if isinstance(y, (int, float)):
            _y = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)
            _y.load_float(y)
        else:
            _y = y

        # resize arguments to target format by multiplying MSB
        # TODO: use _scale function and scale to:
        # max(self.sign_size, y.sign_size), max(self.m_size, y.m_size), max(self.n_size, y.n_size)
        _a = self.hex_value | (self.sign << self.TOTAL_SIZE)
        _b = _y.hex_value | (_y.sign << _y.TOTAL_SIZE)

        # calculate result
        _c = _a + _b
        # _c &= (1 << (self.M_SIZE + self.N_SIZE + self.SIGN_SIZE + 1))-1 # mask is already in load_hex - no need here
        _res = FXPQNumber(self.SIGN_SIZE, max(self.M_SIZE, _y.M_SIZE)+1, self.N_SIZE, _c)
        return _res

    # TODO: add __r* to all types (to support constants on the left side of operation)
    __radd__ = __add__

    def __sub__(self, y):
        # resize arguments to target format by multiplying MSB
        _a = self.hex_value | (self.sign << self.TOTAL_SIZE)
        _b = y.hex_value | (y.sign << y.TOTAL_SIZE)

        # calculate result
        _c = _a - _b
        _res = FXPQNumber(self.SIGN_SIZE, max(self.M_SIZE, y.M_SIZE)+1, self.N_SIZE, _c)
        return _res

    def __mul__(self, y):
        # resize arguments to target format by multiplying MSB
        _new_size = self.N_SIZE + self.M_SIZE + y.M_SIZE + y.N_SIZE # + max([self.SIGN_SIZE != 0, y.SIGN_SIZE])

        _mask = (-1 << (self.N_SIZE + self.M_SIZE)) & ((1 << _new_size)-1)
        _mask *= self.sign
        _a = self.hex_value | _mask

        _mask = (-1 << (y.N_SIZE + y.M_SIZE)) & ((1 << _new_size)-1)
        _mask *= y.sign
        _b = y.hex_value | _mask

        # calculate result
        _c = _a * _b
        _res = FXPQNumber(max([self.SIGN_SIZE, y.SIGN_SIZE]), self.M_SIZE+y.M_SIZE, self.N_SIZE+y.N_SIZE, _c)
        return _res

# a complex number in Q format
class FXPQComplex():
    # re[Q(SIGN.M.N)], img[Q(SIGN.M.N)]
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0, complex_value=complex(0, 0)):
        self.SIGN_SIZE = SIGN_SIZE  # TODO: check which sizes are needed in this class
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE
        self.TOTAL_SIZE = SIGN_SIZE + M_SIZE + N_SIZE

        self.qRE = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)
        self.qIMG = FXPQNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)

        if hex_value:
            self.load_hex(hex_value)
        elif complex_value:
            self.load_float(complex_value)

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

    def sym_round(self, round_factor):
        _re = self.qRE.sym_round(round_factor)
        _img = self.qIMG.sym_round(round_factor)
        _hex_value = (_img.to_hex() << _img.TOTAL_SIZE) | _re.to_hex()
        return FXPQComplex(_re.SIGN_SIZE, _re.M_SIZE, _re.N_SIZE, _hex_value)

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

    def __add__(self, y):
        _res_RE = self.qRE + y.qRE
        _res_IMG = self.qIMG + y.qIMG
        _hex_value = (_res_IMG.to_hex() << (self.TOTAL_SIZE + 1)) | _res_RE.to_hex()
        return FXPQComplex(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _hex_value)

    def __sub__(self, y):
        _res_RE = self.qRE - y.qRE
        _res_IMG = self.qIMG - y.qIMG
        _hex_value = (_res_IMG.to_hex() << (self.TOTAL_SIZE + 1)) | _res_RE.to_hex()
        return FXPQComplex(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _hex_value)

    def __mul__(self, y):
        # calculate RE and IMG part
        _res_RE = self.qRE*y.qRE - self.qIMG*y.qIMG
        _res_IMG = self.qRE*y.qIMG + self.qIMG*y.qRE

        # resize is needed as +/- operation increased m_size 1 bit too much
        _res_RE.resize(_res_RE.SIGN_SIZE, _res_RE.M_SIZE-1, _res_RE.N_SIZE)
        _res_IMG.resize(_res_IMG.SIGN_SIZE, _res_IMG.M_SIZE-1, _res_IMG.N_SIZE)

        # pack and return
        _hex_value = (_res_IMG.to_hex() << _res_RE.TOTAL_SIZE) | _res_RE.to_hex()
        return FXPQComplex(_res_RE.SIGN_SIZE, _res_RE.M_SIZE, _res_RE.N_SIZE, _hex_value)

