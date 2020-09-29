class QNumber():
    def __init__(self, SIGN_SIZE, M_SIZE, N_SIZE, hex_value=0):
        # Q(SIGN.M.N)
        self.SIGN_SIZE = SIGN_SIZE
        self.M_SIZE=M_SIZE
        self.N_SIZE=N_SIZE

        self.hex_value = hex_value
        self.sign = 0
        self.m = 0
        self.n = 0

        self.load_hex(self.hex_value)

    def load_hex(self, h):
        self.hex_value = h

        # extract values
        if self.SIGN_SIZE:
            _sign = (h >> (self.M_SIZE + self.N_SIZE)) & 1
        else:
            _sign = 0

        if _sign:
            _sign_mask = ((1 << (self.N_SIZE + self.M_SIZE))-1)
            h &= _sign_mask     # get value without sign
            h ^= _sign_mask     # invert all bits
            h += 1              # add 1 (U2 conversion)
            self.sign = -1
        else:
            self.sign = 1

        if self.M_SIZE:
            self.m = (h >> self.N_SIZE) & ((1 << self.M_SIZE)-1)
        else:
            self.m = 0

        if self.N_SIZE:
            self.n = h & ((1 << self.N_SIZE)-1)
        else:
            self.n = 0

    def load_float(self, value):
        _tmp = int(round(value * (1 << self.N_SIZE)))
        # truncate MSbits - this will also convert to unsigned format
        _tmp = _tmp & ( (1 << (self.N_SIZE + self.M_SIZE + self.SIGN_SIZE)) - 1)
        self.load_hex(_tmp)

    def load_Q(self, sign, m, n):
        # sing MUST be 1 or -1 !
        self.sign = sign
        self.m = m
        self.n = n

    def get_hex(self):
        return self.hex_value

    def get_float(self):
        _res = self.sign*(self.m + self.n / (1 << self.N_SIZE))
        return _res

    def normalize(self, val):
        # TODO - a more complicated as require to change digit format
        # maybe return hex value instead of changing?
        _tmp = self.hex >> val
        self.load_hex(_tmp)

    def print_as_Q(self):
        print (self.sign)
        print (self.m, bin(self.m))
        print (self.n, bin(self.n))

    def print_as_float(self):
        print("float:", self.get_float())

# a complex number in Q format
class QComplex():
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

    def get_hex(self):
        _tmp = 0
        _tmp |= self.qRE.get_hex()
        _tmp |= self.qIMG.get_hex() << self.TOTAL_SIZE
        return _tmp

    def get_float(self):
        _re = self.qRE.get_float()
        _img = self.qIMG.get_float()
        return complex(_re, _img)

