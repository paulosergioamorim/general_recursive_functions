class PrimitiveRecursive:
    ninputs = 1
    noutputs = 1

    def __call__(self, *args, **kargs):
        args = args
        kargs = kargs
        raise NotImplementedError()

class Successor(PrimitiveRecursive):
    def __call__(self, x: int) -> int:
        return x+1

    def __str__(self) -> str:
        return "(x -> x+1)"

class Zero(PrimitiveRecursive):
    def __call__(self, _: int) -> int:
        return 0

    def __str__(self) -> str:
        return "(x -> 0)"

class ZeroNoArgs(PrimitiveRecursive):
    def __init__(self):
        self.ninputs = 0

    def __call__(self) -> int:
        return 0

    def __str__(self) -> str:
        return "0"

class Proj(PrimitiveRecursive):
    def __init__(self, n: int, i: int):
        self.ninputs = n
        self.i = i

    def __call__(self, *xs: int) -> int:
        assert len(xs) == self.ninputs
        assert self.i >= 1 and self.i <= len(xs)
        ii = self.i-1
        return xs[ii]

    def __str__(self) -> str:
        if self.ninputs == 1:
            return "(x1 -> x1)"
        return f"(x1,...,x{self.ninputs} -> x{self.i})"

class Composition(PrimitiveRecursive):
    def __init__(self, g: PrimitiveRecursive, h: PrimitiveRecursive):
        assert h.noutputs == g.ninputs
        self.g = g
        self.h = h
        self.ninputs = h.ninputs
        self.noutputs = g.noutputs

    def __call__(self, *xs: int) -> int:
        if type(self.h) == Tuple:
            return self.g(*self.h(*xs))
        return self.g(self.h(*xs))

    def __str__(self) -> str:
        return f"({self.g} . {self.h})"

class Ro(PrimitiveRecursive):
    def __init__(self, g: PrimitiveRecursive, h: PrimitiveRecursive):
        assert g.ninputs + 2 == h.ninputs
        self.g = g
        self.h = h
        self.ninputs = g.ninputs + 1

    def __call__(self, *xs: int) -> int:
        f = self
        x0 = xs[0]
        if x0 == ZeroNoArgs()():
            return self.g(*xs[1:])
        return self.h(*[x0-1, f(*[x0-1, *xs[1:]]), *xs[1:]])

    def __str__(self) -> str:
        return f"(ro({self.g},{self.h}))"

class Tuple(PrimitiveRecursive):
    def __init__(self, *fs: PrimitiveRecursive):
        for f in fs:
            assert f.ninputs == fs[0].ninputs
        self.fs = fs
        self.ninputs = fs[0].ninputs
        self.noutputs = len(fs)

    def __call__(self, *xs: int) -> tuple[int]:
        return tuple([f(*xs) for f in self.fs])

    def __str__(self) -> str:
        args_str = f"x1,...,x{self.ninputs}"
        return f"{args_str} -> ({self.fs[0]}({args_str}),...,{self.fs[-1]}({args_str}))"

def Constant(n: int, k: int) -> PrimitiveRecursive:
    if n == 0:
        if k == 0:
            return ZeroNoArgs()
        return Composition(Successor(), Constant(0, k-1))
    if k == 0:
        return Composition(Zero(), Proj(n, 1))
    return Composition(Successor(), Constant(n, k-1))

Sum = Ro(Proj(1,1), Composition(Successor(), Proj(3,2)))
assert Sum(3,5) == 8

Pred = Ro(ZeroNoArgs(), Proj(2,1))
assert Pred(0) == 0
assert Pred(2) == 1

Swap = Tuple(Proj(2,2), Proj(2,1))
assert Swap(1,2) == (2,1)

RSub = Ro(Proj(1,1), Composition(Pred, Proj(3,2)))
Sub = Composition(RSub, Swap)
assert Sub(4,9) == 0
assert Sub(9,4) == 5

Mul = Ro(Zero(), Composition(Sum, Tuple(Proj(3,2), Proj(3,3))))
assert Mul(5,6) == 30

If = Ro(Proj(2,2), Proj(4,3))
assert If(0,8,9) == 9
assert If(1,8,9) == 8

And = Composition(If, Tuple(Proj(2,1), Proj(2,2), Constant(2,0)))
assert And(0,0) == 0
assert And(1,0) == 0
assert And(0,1) == 0
assert And(1,1) == 1

Or = Composition(If, Tuple(Proj(2,1), Constant(2,1), Proj(2,2)))
assert Or(0,0) == 0
assert Or(0,1) == 1
assert Or(1,0) == 1
assert Or(1,1) == 1

IsZero = Ro(Constant(0, 1), Constant(2, 0))
Not = IsZero
assert IsZero(0) == 1
assert IsZero(1) == 0

RExp = Ro(Constant(1,1), Composition(Mul, Tuple(Proj(3,2), Proj(3,3))))
Exp = Composition(RExp, Swap)
assert Exp(2,6) == 64

Leq = Composition(IsZero, Sub)
assert Leq(9,8) == 0
assert Leq(8,9) == 1
assert Leq(8,8) == 1

Geq = Composition(Leq, Swap)
assert Geq(9,8) == 1
assert Geq(8,9) == 0
assert Geq(8,8) == 1

Eq = Composition(And, Tuple(Leq, Geq))
assert Eq(9,8) == 0
assert Eq(8,8) == 1
assert Eq(7,8) == 0

Fac = Ro(Constant(0,1), Composition(Mul, Tuple(Composition(Successor(), Proj(2,1)), Proj(2,2))))
assert Fac(6) == 720

Rest = Ro(Zero(), Composition(If, Tuple(
    Composition(Eq, Tuple(Composition(Pred, Proj(3,3)), Proj(3,2))),
    Constant(3,0),
    Composition(Successor(), Proj(3,2))
)))

for i in range(0, 30):
    assert Rest(i,5) == i % 5

Div = Ro(Zero(), Composition(If, Tuple(
    Composition(Eq, Tuple(Composition(Pred, Proj(3,3)), Composition(Rest, Tuple(Proj(3,1), Proj(3,3))))),
    Composition(Successor(), Proj(3,2)),
    Proj(3,2)
)))

for i in range(0, 30):
    assert Div(i,5) == int(i / 5)

print(Sum)
