"""
Linear codes
"""

from .Zmod import Zmod
from .GF2 import GF2
from .poly import Poly
from .la import Matrix, eye, zeros


def poly2bits(x: Poly) -> list:
    "Convert a polynomial in GF(2^n)[x] to a list of binary digits."
    out = []
    for c in x.coeff:
        out += c.bits()
    return out

def left_standard_form(M: Matrix) -> (Matrix, Matrix):
    "Compute the left standard form of a generator matrix. Return the standard form and the pertmutation matrix."
    # reduced row echelon form
    M = M.rref()
    # purge zero rows
    for i in range(M.rows-1,-1,-1):
        if not M[i,:]:
            M.delete_rows(i)
    # permute columns to get the identity on the left
    last = min(M.rows, M.cols)
    P = eye(M.cols)
    for i in range(last):
        if not M[i,i]: # the diagonal entry vanishes
            # find the index of the pivot and permute
            j = i + 1
            while j <= M.cols and not M[i, j]:
                j += 1
            P[:,i], P[:,j] = P[:,j], P[:,i]
            M[:,i], M[:,j] = M[:,j], M[:,i]
    return M, P

def gen2pchk(G: Matrix) -> Matrix:
    "Compute the parity check matrix from a given generator matrix (and vice versa)."
    G, P = left_standard_form(G)
    d = G.cols - G.rows
    if d <= 0:
        raise ValueError("A generator matrix must have more columns than rows!")
    zero = 0 * G[0]
    one = zero**0
    # we start with a zero matrix
    H = zeros(d, G.cols, zero = zero)
    # create the identity on the right
    for i in range(d):
        H[i,G.rows+i] = one
    # add minus the transpose of the right part of G as the left part
    tmp = - G[:,-d:].transpose()
    for i in range(G.cols - d):
        H[:, i] = tmp[:, i]
    return H * P.transpose()

def hamming_dist(a: iter, b: iter):
    "Hamming distance of two iterables."
    if len(a) != len(b):
        raise ValueError("Both iteralbles must have equal length.")
    return sum(aa != bb for aa, bb in zip(a, b))

class Goppa():
    """
    Binary irreducible Goppa code.

    Example:

    >>> gf = GF2(4) # base field GF(2^n)
    >>> g = Poly([2, 0, 0, 1], ring = gf) # irreducible Polynomial for the code
    >>> alpha = list(gf) # list of points from the base field (must not contain zeros of g)
    >>> goppa = Goppa(gf, g, alpha)
    
    To encode a list of bits (the length must be equal to the dimension k of the code)
    >>> goppa.encode([1, 0, 1, 1])
    [0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1]

    Decoding still works if there are at most deg(g) errors:
    >>> goppa.decode([0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 0])
    [1, 0, 1, 1]
    
    """

    def __init__(self, gf: GF2, g: Poly, alpha: list["GF2Point"]):
        if not all(map(lambda x: x in gf, alpha)):
            raise ValueError(f"{x}: alpha must be a list of elements from the Galois field!")
        if not g.rabin_test():
            raise ValueError(f"The polynomial g must be irreducible!")
        self.gf = gf  # underlying Galois field
        self.g = g  # polynomial
        self.alpha = alpha # list of elements from gf
        # Compute the control matrix
        self.Z_2 = Zmod(2)

        tmp =[]
        for x in alpha:
            tmp.append(Poly([-x, 1], ring = gf, modulus = g).inv().bits())
        self.H = Matrix(tmp, ring=self.Z_2).transpose()
        # Compute the generator matrix
        self.G = gen2pchk(self.H)

    def __repr__(self):
        return f"Binary irreducible Goppa code over GF(2^{self.gf.power}) with polynomial g(x) = {self.g}."

    def encode(self, x: list[int]):
        "Encode a given list of bits."
        x = Matrix(x, ring = self.Z_2)
        y = self.G.transpose() * x
        y.map(int)
        return list(y)

    def decode(self, y: list[int]):
        "Decode a given list of bits."
        y = Matrix(y, ring = self.Z_2)
        if self.H * y: # no code word
            s = self.gf(0) # syndrom polynomial
            for i, x in enumerate(self.alpha):
                s += int(y[i]) * Poly([-x, 1], ring = self.gf, modulus = self.g).inv()
            v = (s.inv() - Poly([0, 1], ring = self.gf, modulus = self.g))**(self.gf.order ** self.g.degree() // 2)
            # determine error locator polynomial sigma(x) = a(x^2) + b(x^2) * x
            # find a and b by running EEA until b has the desired degree
            v.modulus = None
            r0, r1 = self.g, v
            y0, y1 = Poly([self.gf(0)]), Poly([self.gf(1)])
            while 2 * r1.degree() > self.g.degree():
                q, r = r0.divmod(r1)
                r0, r1 = r1, r
                y0, y1 = y1, y0 - q * y1
            a, b = r1, y1
            sigma = a**2 + b**2 * Poly([0,1], ring = self.gf)
            # correct the error
            for x in self.alpha:
                if not sigma(x):
                    y[int(x)] += 1
            if self.H * y:
                raise ValueError("Decoding failed!")
        x = self.G.transpose().solve(y)
        x.map(int)
        return list(x)