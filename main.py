class GeneralRecursive:
    ninputs = 1

    def __call__(self, *_: int) -> int:
        raise NotImplementedError()


class PrimitiveRecursive(GeneralRecursive):
    pass


"""
Basic Primitive Recursive Functions Set
"""


class Successor(PrimitiveRecursive):
    def __call__(self, *xs: int) -> int:
        """
        S(x) = x+1
        """
        assert len(xs) == 1
        assert xs[0] >= 0
        return xs[0] + 1

    def __str__(self) -> str:
        return "S"


class Constant(PrimitiveRecursive):
    def __init__(self, n: int, k: int):
        """
        n: n-ary function
        k: non-negative integer to be returned
        """
        assert n >= 0
        assert k >= 0
        self.ninputs = n
        self.k = k

    def __call__(self, *xs: int) -> int:
        """
        C^n_k(x1,...,xn) = k
        """
        assert len(xs) == self.ninputs
        return self.k

    def __str__(self) -> str:
        return f"C^{self.ninputs}_{self.k}"


class Proj(PrimitiveRecursive):
    def __init__(self, n: int, i: int):
        """
        n: n-ary function
        i: 1-index based argument to be returned
        """
        assert i >= 1 and i <= n
        self.ninputs = n
        self.i = i

    def __call__(self, *xs: int) -> int:
        """
        P^n_i(x1,...,xn) = xi
        """
        assert len(xs) == self.ninputs
        return xs[self.i - 1]

    def __str__(self) -> str:
        return f"P^{self.ninputs}_{self.i}"


"""
Alternative definition uses Zero function and builts all constant functions with Zero, Successor, and Proj
"""
Zero = Constant(1, 0)
ZeroNoArgs = Constant(0, 0)


"""
Primitive Recursive Operators: Composition and Rho
"""


class Composition(GeneralRecursive):
    def __init__(self, h: GeneralRecursive, *gs: GeneralRecursive):
        """
        h: n-ary function
        gs: n k-ary functions
        """
        assert len(gs) == h.ninputs
        for g in gs:
            assert g.ninputs == gs[0].ninputs
        self.h = h
        self.gs = gs
        self.ninputs = gs[0].ninputs

    def __call__(self, *xs: int) -> int:
        """
        f(x1,...,xk) = h(g1(x1,...,xk),...,gn(x1,...,xk))
        """
        return self.h(*(g(*xs) for g in self.gs))

    def __str__(self) -> str:
        if len(self.gs) == 1:
            return f"({self.h} . {self.gs[0]})"
        return f"({self.h} . ({', '.join([str(g) for g in self.gs])})"


class Rho(GeneralRecursive):
    def __init__(self, g: GeneralRecursive, h: GeneralRecursive):
        """
        g: n-ary function
        h: (n+2)-ary function
        """
        assert g.ninputs + 2 == h.ninputs
        self.g = g
        self.h = h
        self.ninputs = g.ninputs + 1

    def __call__(self, *xs: int) -> int:
        """
        f(x,y1,...,yn) =
            g(y1,...,yn)                      , if x == 0
            h(x-1,f(x-1,y1,...,yn),y1,...,yn) , otherwise
        """
        return (
            self.g(*xs[1:])
            if xs[0] == 0
            else self.h(*[xs[0] - 1, self(*[xs[0] - 1, *xs[1:]]), *xs[1:]])
        )

    def __str__(self) -> str:
        return f"\u03c1({self.g}, {self.h})"


"""
Mi-Recursive Operator
"""


class Mi(GeneralRecursive):
    def __init__(self, f: GeneralRecursive):
        """
        f: (n+1)-ary function
        """
        assert (f.ninputs) >= 1
        self.f = f
        self.ninputs = f.ninputs - 1

    def __call__(self, *xs: int) -> int:
        """
        mi(f)(x1,...,xn) = max z st. f(z',x1,...,xn) > 0 for z' < z and f(z,x1,...,xn) = 0
        """
        assert len(xs) == self.ninputs
        z = 0
        while self.f(*[z, *xs]) != 0:
            z += 1
        return z

    def __str__(self) -> str:
        return f"\u00b5({self.f})"


"""
Sum(0,y)   = y
Sum(x+1,y) = x+1+y = S(Sum(x,y))
"""
Sum = Rho(Proj(1, 1), Composition(Successor(), Proj(3, 2)))
assert Sum(3, 5) == 8

"""
Pred(0)   = 0
Pred(x+1) = x
"""
Pred = Rho(Constant(0, 0), Proj(2, 1))
assert Pred(0) == 0
assert Pred(2) == 1

Swap = Proj(2, 2), Proj(2, 1)

"""
RSub(0,y)   = y-0     = y
RSub(x+1,y) = y-(x+1) = y-x-1 = Pred(RSub(x,y))
"""
RSub = Rho(Proj(1, 1), Composition(Pred, Proj(3, 2)))
Sub = Composition(RSub, *Swap)
assert Sub(4, 9) == 0
assert Sub(9, 4) == 5

"""
Mul(0,y)   = 0
Mul(x+1,y) = (x+1)*y = x*y+y = Sum(Mul(x,y), y)
"""
Mul = Rho(Constant(1, 0), Composition(Sum, Proj(3, 2), Proj(3, 3)))
assert Mul(5, 6) == 30
assert Mul(5, 0) == 0

"""
If(0,y,z)   = z
If(x+1,y,z) = y
"""
If = Rho(Proj(2, 2), Proj(4, 3))
assert If(0, 8, 9) == 9
assert If(1, 8, 9) == 8

And = Composition(If, Proj(2, 1), Proj(2, 2), Constant(2, 0))
assert And(0, 0) == 0
assert And(1, 0) == 0
assert And(0, 1) == 0
assert And(1, 1) == 1

Or = Composition(If, Proj(2, 1), Constant(2, 1), Proj(2, 2))
assert Or(0, 0) == 0
assert Or(0, 1) == 1
assert Or(1, 0) == 1
assert Or(1, 1) == 1

"""
IsZero(0)   = 1
IsZero(x+1) = 0
"""
IsZero = Rho(Constant(0, 1), Constant(2, 0))
Not = IsZero
assert IsZero(0) == 1
assert IsZero(1) == 0

"""
RExp(0,y)   = y**0 = 1
RExp(x+1,y) = y**(x+1) = y**x * y = Mul(RExp(x,y), y)
"""
RExp = Rho(Constant(1, 1), Composition(Mul, Proj(3, 2), Proj(3, 3)))
Exp = Composition(RExp, *Swap)
assert Exp(2, 6) == 64
assert Exp(2, 0) == 1

"""
Leq(x,y) = 0 <=> Sub(x,y) = 0
"""
Leq = Composition(IsZero, Sub)
assert Leq(9, 8) == 0
assert Leq(8, 9) == 1
assert Leq(8, 8) == 1

Geq = Composition(Leq, *Swap)
assert Geq(9, 8) == 1
assert Geq(8, 9) == 0
assert Geq(8, 8) == 1

Eq = Composition(And, Leq, Geq)
assert Eq(9, 8) == 0
assert Eq(8, 8) == 1
assert Eq(7, 8) == 0

Less = Composition(And, Leq, Composition(Not, Geq))
assert Less(9, 8) == 0
assert Less(8, 9) == 1
assert Less(8, 8) == 0

Gt = Composition(Less, *Swap)
assert Gt(9, 8) == 1
assert Gt(8, 9) == 0
assert Gt(8, 8) == 0

Xor = Composition(And, Or, Composition(Not, Eq))
assert Xor(0, 0) == 0
assert Xor(0, 1) == 1
assert Xor(1, 0) == 1
assert Xor(1, 1) == 0

Nand = Composition(Not, And)
assert Nand(0, 0) == 1
assert Nand(1, 0) == 1
assert Nand(0, 1) == 1
assert Nand(1, 1) == 0

Nor = Composition(Not, Or)
assert Nor(0, 0) == 1
assert Nor(1, 0) == 0
assert Nor(0, 1) == 0
assert Nor(1, 1) == 0

Xnor = Composition(Not, Xor)
assert Xnor(0, 0) == 1
assert Xnor(1, 0) == 0
assert Xnor(0, 1) == 0
assert Xnor(1, 1) == 1

"""
Fac(0)   = 1
Fac(x+1) = (x+1)*Fac(x) = Mul(S(x), Fac(x))
"""
Fac = Rho(
    Constant(0, 1), Composition(Mul, Composition(Successor(), Proj(2, 1)), Proj(2, 2))
)
assert Fac(6) == 720

"""
Rest(0,y)   = 0
Rest(x+1,y) = 
    0             , if y-1 == Rest(x,y)
    1 + Rest(x,y) , otherwise 
"""
Rest = Rho(
    Constant(1, 0),
    Composition(
        If,
        Composition(Eq, Composition(Pred, Proj(3, 3)), Proj(3, 2)),
        Constant(3, 0),
        Composition(Successor(), Proj(3, 2)),
    ),
)

for i in range(0, 30):
    assert Rest(i, 5) == i % 5

"""
Div(0,y)   = 0
Div(x+1,y) = 
    1 + Div(x,y) , if y-1 == Rest(x,y)
        Div(x,y) , otherwise 
"""
Div = Rho(
    Constant(1, 0),
    Composition(
        If,
        Composition(
            Eq,
            Composition(Pred, Proj(3, 3)),
            Composition(Rest, Proj(3, 1), Proj(3, 3)),
        ),
        Composition(Successor(), Proj(3, 2)),
        Proj(3, 2),
    ),
)

for i in range(0, 30):
    assert Div(i, 5) == int(i / 5)

Mod2 = Composition(Rest, Proj(1, 1), Constant(1, 2))

for i in range(0, 30):
    assert Mod2(i) == i % 2

Div3 = Composition(Div, Proj(1, 1), Constant(1, 3))

for i in range(0, 30):
    assert Div3(i) == int(i / 3)

"""
Isqrt(x) = max z st. z**2 <= x.
Incrementa z enquanto (z+1)**2 é <= que a entrada, quando falha, retorna z
"""
Isqrt = Mi(
    Composition(
        Leq,
        Composition(Exp, Composition(Successor(), Proj(2, 1)), Constant(2, 2)),
        Proj(2, 2),
    )
)

assert Isqrt(50) == 7
assert Isqrt(49) == 7
assert Isqrt(48) == 6
assert Isqrt(9) == 3
assert Isqrt(100) == 10

"""
Não existe z tal que C^1_1 retorne 0.
NotHalt entra em loop e não para.
"""
NotHalt = Mi(Constant(1, 1))
# NotHalt()

DoubleIt = Composition(Sum, Proj(1, 1), Proj(1, 1))
assert DoubleIt(0) == 0
assert DoubleIt(8) == 16

print(Sub)
