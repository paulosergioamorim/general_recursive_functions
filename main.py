class GeneralRecursive:
    ninputs = 1
    noutputs = 1

    def __call__(self, *args, **kargs):
        args = args
        kargs = kargs
        raise NotImplementedError()


class PrimitiveRecursive(GeneralRecursive):
    pass


"""
Basic Primitive Recursive Functions Set
"""


class Successor(PrimitiveRecursive):
    def __call__(self, x: int) -> int:
        assert x >= 0
        return x + 1

    def __str__(self) -> str:
        return "S"


class Constant(PrimitiveRecursive):
    def __init__(self, n: int, k: int):
        assert n >= 0
        assert k >= 0
        self.ninputs = n
        self.k = k

    def __call__(self, *xs: int) -> int:
        assert len(xs) == self.ninputs
        return self.k

    def __str__(self) -> str:
        return f"C^{self.ninputs}_{self.k}"


class Proj(PrimitiveRecursive):
    def __init__(self, n: int, i: int):
        assert i >= 1 and i <= n
        self.ninputs = n
        self.i = i

    def __call__(self, *xs: int) -> int:
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
    def __init__(self, g: GeneralRecursive, h: GeneralRecursive):
        assert h.noutputs == g.ninputs
        self.g = g
        self.h = h
        self.ninputs = h.ninputs
        self.noutputs = g.noutputs

    def __call__(self, *xs: int) -> int:
        return self.g(*self.h(*xs)) if type(self.h) == Tuple else self.g(self.h(*xs))

    def __str__(self) -> str:
        return f"({self.g} . {self.h})"


class Rho(GeneralRecursive):
    def __init__(self, g: GeneralRecursive, h: GeneralRecursive):
        assert g.ninputs + 2 == h.ninputs
        self.g = g
        self.h = h
        self.ninputs = g.ninputs + 1

    def __call__(self, *xs: int) -> int:
        return (
            self.g(*xs[1:])
            if xs[0] == 0
            else self.h(*[xs[0] - 1, self(*[xs[0] - 1, *xs[1:]]), *xs[1:]])
        )

    def __str__(self) -> str:
        return f"\u03c1({self.g}, {self.h})"


class Tuple(GeneralRecursive):
    """
    General recursive function that returns multiple values
    """

    def __init__(self, *fs: GeneralRecursive):
        for f in fs:
            assert f.ninputs == fs[0].ninputs
        self.fs = fs
        self.ninputs = fs[0].ninputs
        self.noutputs = len(fs)

    def __call__(self, *xs: int) -> tuple[int]:
        return tuple([f(*xs) for f in self.fs])

    def __str__(self) -> str:
        outputs_str = ", ".join([f"{f}" for f in self.fs])
        return f"({outputs_str})"


class Mi(GeneralRecursive):
    def __init__(self, f: GeneralRecursive):
        self.f = f
        self.ninputs = f.ninputs - 1

    def __call__(self, *xs: int) -> int:
        assert len(xs) == self.ninputs
        z = 0
        while self.f(*[z, *xs]) != 0:
            z += 1
        return z

    def __str__(self) -> str:
        return f"\u00b5({self.f})"


Sum = Rho(Proj(1, 1), Composition(Successor(), Proj(3, 2)))
assert Sum(3, 5) == 8

Pred = Rho(Constant(0, 0), Proj(2, 1))
assert Pred(0) == 0
assert Pred(2) == 1

Swap = Tuple(Proj(2, 2), Proj(2, 1))
assert Swap(1, 2) == (2, 1)

RSub = Rho(Proj(1, 1), Composition(Pred, Proj(3, 2)))
Sub = Composition(RSub, Swap)
assert Sub(4, 9) == 0
assert Sub(9, 4) == 5

Mul = Rho(Constant(1, 0), Composition(Sum, Tuple(Proj(3, 2), Proj(3, 3))))
assert Mul(5, 6) == 30
assert Mul(5, 0) == 0

If = Rho(Proj(2, 2), Proj(4, 3))
assert If(0, 8, 9) == 9
assert If(1, 8, 9) == 8

And = Composition(If, Tuple(Proj(2, 1), Proj(2, 2), Constant(2, 0)))
assert And(0, 0) == 0
assert And(1, 0) == 0
assert And(0, 1) == 0
assert And(1, 1) == 1

Or = Composition(If, Tuple(Proj(2, 1), Constant(2, 1), Proj(2, 2)))
assert Or(0, 0) == 0
assert Or(0, 1) == 1
assert Or(1, 0) == 1
assert Or(1, 1) == 1

IsZero = Rho(Constant(0, 1), Constant(2, 0))
Not = IsZero
assert IsZero(0) == 1
assert IsZero(1) == 0

RExp = Rho(Constant(1, 1), Composition(Mul, Tuple(Proj(3, 2), Proj(3, 3))))
Exp = Composition(RExp, Swap)
assert Exp(2, 6) == 64
assert Exp(2, 0) == 1

Leq = Composition(IsZero, Sub)
assert Leq(9, 8) == 0
assert Leq(8, 9) == 1
assert Leq(8, 8) == 1

Geq = Composition(Leq, Swap)
assert Geq(9, 8) == 1
assert Geq(8, 9) == 0
assert Geq(8, 8) == 1

Eq = Composition(And, Tuple(Leq, Geq))
assert Eq(9, 8) == 0
assert Eq(8, 8) == 1
assert Eq(7, 8) == 0

Less = Composition(And, Tuple(Leq, Composition(Not, Geq)))
assert Less(9, 8) == 0
assert Less(8, 9) == 1
assert Less(8, 8) == 0

Gt = Composition(Less, Swap)
assert Gt(9, 8) == 1
assert Gt(8, 9) == 0
assert Gt(8, 8) == 0

Xor = Composition(And, Tuple(Or, Composition(Not, Eq)))
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

Fac = Rho(
    Constant(0, 1),
    Composition(Mul, Tuple(Composition(Successor(), Proj(2, 1)), Proj(2, 2))),
)
assert Fac(6) == 720

Rest = Rho(
    Constant(1, 0),
    Composition(
        If,
        Tuple(
            Composition(Eq, Tuple(Composition(Pred, Proj(3, 3)), Proj(3, 2))),
            Constant(3, 0),
            Composition(Successor(), Proj(3, 2)),
        ),
    ),
)

for i in range(0, 30):
    assert Rest(i, 5) == i % 5

Div = Rho(
    Constant(1, 0),
    Composition(
        If,
        Tuple(
            Composition(
                Eq,
                Tuple(
                    Composition(Pred, Proj(3, 3)),
                    Composition(Rest, Tuple(Proj(3, 1), Proj(3, 3))),
                ),
            ),
            Composition(Successor(), Proj(3, 2)),
            Proj(3, 2),
        ),
    ),
)

for i in range(0, 30):
    assert Div(i, 5) == int(i / 5)

Mod2 = Composition(Rest, Tuple(Proj(1, 1), Constant(1, 2)))

for i in range(0, 30):
    assert Mod2(i) == i % 2

Div3 = Composition(Div, Tuple(Proj(1, 1), Constant(1, 3)))

for i in range(0, 30):
    assert Div3(i) == int(i / 3)

Isqrt = Mi(
    Composition(
        Not,
        Composition(
            Gt,
            Tuple(
                Composition(
                    Mul,
                    Tuple(
                        Composition(Successor(), Proj(2, 1)),
                        Composition(Successor(), Proj(2, 1)),
                    ),
                ),
                Proj(2, 2),
            ),
        ),
    )
)

assert Isqrt(50) == 7
assert Isqrt(49) == 7
assert Isqrt(48) == 6

NotHalt = Mi(Constant(1, 1))
# NotHalt()

print(Sub)
