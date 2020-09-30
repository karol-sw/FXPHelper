class FXPQNumber():
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0):
        # Q(SIGN.M.N)
        self.SIGN_SIZE = SIGN_SIZE
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE
        self.TOTAL_SIZE=SIGN_SIZE + M_SIZE + N_SIZE

        self.hex_value = 0
        self.sign = 0

        self.load_hex(hex_value)

    def load_hex(self, h):
        _mask = (1 << self.TOTAL_SIZE)-1
        self.hex_value = h & _mask

        # extract sign
        if self.SIGN_SIZE:
            self.sign = (h >> (self.M_SIZE + self.N_SIZE)) & 1
        else:
            self.sign = 0

    def load_float(self, value):
        _tmp = int(round(value * (1 << self.N_SIZE)))
        # truncate MSbits - this will also convert to unsigned format
        #_tmp = _tmp & ( (1 << (self.N_SIZE + self.M_SIZE + self.SIGN_SIZE)) - 1)
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


    # a little hack is here - by default __str__ in numpy for unknown types displays
    # a type - so we will override a type return value to get a real number value
    def __repr__(self):
        return str(hex(self.hex_value))

    def __str__(self):
        return str(hex(self.hex_value))

    def __add__(self, y):
        # resize arguments to target format by multiplying MSB
        _a = self.hex_value | (self.sign << self.TOTAL_SIZE)
        _b = y.hex_value | (y.sign << y.TOTAL_SIZE)

        # calculate result
        _c = _a + _b
        # _c &= (1 << (self.M_SIZE + self.N_SIZE + self.SIGN_SIZE + 1))-1 # mask is already in load_hex - no need here
        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _c)
        return _res

    def __sub__(self, y):
        # resize arguments to target format by multiplying MSB
        _a = self.hex_value | (self.sign << self.TOTAL_SIZE)
        _b = y.hex_value | (y.sign << y.TOTAL_SIZE)

        # calculate result
        _c = _a - _b
        # _c &= (1 << (self.M_SIZE + self.N_SIZE + self.SIGN_SIZE + 1))-1 # mask is already in load_hex - no need here
        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _c)
        return _res

    def __mul__(self, y):
        # TODO:not working for signed numbers!
        _res = FXPQNumber(self.SIGN_SIZE, self.M_SIZE+y.M_SIZE, self.N_SIZE+y.N_SIZE)
        _res.load_hex(self.hex_value * y.to_hex())
        return _res

# a complex number in Q format
class FXPQComplex():
    # re[Q(SIGN.M.N)], img[Q(SIGN.M.N)]
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0):
        self.SIGN_SIZE = SIGN_SIZE
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE
        self.TOTAL_SIZE = SIGN_SIZE + M_SIZE + N_SIZE

        self.qRE = FXP_QNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)
        self.qIMG = FXP_QNumber(self.SIGN_SIZE, self.M_SIZE, self.N_SIZE)

        self.load_hex(hex_value)

    def load_hex(self, h):
        _mask = (1 << self.TOTAL_SIZE) - 1
        _re = h & _mask
        _img = (h >> self.TOTAL_SIZE) & _mask
        self.qRE.load_hex(_re)
        self.qIMG.load_hex(_img)

    def load_float(self, re_value, img_value):
        self.qRE.load_float(re_value)
        self.qIMG.load_float(img_value)

    def to_hex(self):
        _tmp = 0
        _tmp |= self.qRE.to_hex()
        _tmp |= self.qIMG.to_hex() << self.TOTAL_SIZE
        return _tmp

    def to_float(self):
        _re = self.qRE.to_float()
        _img = self.qIMG.to_float()
        return complex(_re, _img)

    def __repr__(self):
        # return "{:x} +j{:x}".format(self.qRE.to_hex(), self.qIMG.to_hex())
        return str(complex(self.qRE.to_float(), self.qIMG.to_float()))

    def __str__(self):
        return str(complex(self.qRE.to_float(), self.qIMG.to_float()))

    def __add__(self, y):
        _res_RE = self.qRE + y.qRE
        _res_IMG = self.qIMG + y.qIMG
        _hex_value = (_res_IMG.to_hex() << (self.TOTAL_SIZE + 1)) | _res_RE.to_hex()
        return FXP_QComplex(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _hex_value)

    def __sub__(self, y):
        _res_RE = self.qRE - y.qRE
        _res_IMG = self.qIMG - y.qIMG
        _hex_value = (_res_IMG.to_hex() << (self.TOTAL_SIZE + 1)) | _res_RE.to_hex()
        return FXP_QComplex(self.SIGN_SIZE, self.M_SIZE+1, self.N_SIZE, _hex_value)

    def __mul__(self, y):
        return 4