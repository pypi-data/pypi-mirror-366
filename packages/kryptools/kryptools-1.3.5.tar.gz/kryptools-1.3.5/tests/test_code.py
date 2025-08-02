import pytest
from random import randint, seed
from kryptools import Zmod, GF2, Poly, Matrix
from kryptools import gen2pchk, Goppa

seed(0)
Z_2 = Zmod(2)

def Hamming2(h: int) -> Matrix:
    "Parity check matrix for the binary Hamming code."
    out = []
    for i in range(1,2**h):
        out.append([int(d) for d in str(format(i, "0" + str(h) + "b"))])
    return Matrix(out, ring = Z_2).transpose()


def test_gen2pchk():
    for h in range(2,6):
        H = Hamming2(h)
        G = gen2pchk(H)
        assert not H * G.transpose()

num_tests = 10

def test_Goppa():
    for gf, t in [ [GF2(4), 3],  [GF2(6), 4]]:
        found = False
        while not found:
            c = [randint(0,gf.order-1) for _ in range(t)] + [1]
            g = Poly(c, ring = gf)
            found = g.rabin_test()
        alpha = list(gf)

        goppa = Goppa(gf, g, alpha)
        for _ in range(num_tests):
            x = [ randint(0,1) for _ in range(goppa.G.rows) ]
            y = goppa.encode(x)
            for _ in range(t):
                i = randint(0, goppa.G.cols-1)
                y[i] = 1- y[i]
            assert goppa.decode(y) == x
