import numpy as np


class Quantity:
    def __init__(self, **kwargs):
        if kwargs:
            try:
                key = list(kwargs.keys())[0]
                value = list(kwargs.values())[0]
                if isinstance(value, (list, tuple)):
                    value = np.array(value)
                setattr(self, key, value)
            except:
                raise ValueError("Invalid argument.")

    @property
    def initial(self):
        if isinstance(self.si, np.ndarray):
            return type(self)(si=[col[0] for col in self.si])
        return type(self)(si=self.si[0])
        
    @property
    def final(self):
        if isinstance(self.si, np.ndarray):
            return type(self)(si=[col[-1] for col in self.si])
        return type(self)(si=self.si[-1])
    
    @property
    def size(self):
        if isinstance(self.si, np.ndarray):
            return self.si.size
        return 1
    
    def __getitem__(self, index):
        return type(self)(si=self.si[index])

    def __add__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si + other.si
        return type(self)(si=si)

    def __radd__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si + self.si
        return type(self)(si=si)

    def __sub__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si - other.si
        return type(self)(si=si)

    def __rsub__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si - self.si
        return type(self)(si=si)

    def __mul__(self, other):
        from .unitless import Unitless

        if not isinstance(other, Quantity):
            other = Unitless(si=other)
            # other = Quantity(si=other)
        si = self.si * other.si
        if isinstance(other, Unitless):
            return type(self)(si=si)
        if isinstance(self, Unitless):
            return type(other)(si=si)
        return Quantity(si=si)

    def __rmul__(self, other):
        from .unitless import Unitless

        if not isinstance(other, Quantity):
            other = Unitless(si=other)
            # other = Quantity(si=other)
        si = other.si * self.si
        if isinstance(other, Unitless):
            return type(self)(si=si)
        if isinstance(self, Unitless):
            return type(other)(si=si)
        return Quantity(si=si)

    def __truediv__(self, other):
        from .unitless import Unitless

        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = np.divide(self.si, other.si)
        if isinstance(other, Unitless):
            return type(self)(si=si)
        if type(other) is type(self) and not type(self) is Quantity:
            return Unitless(si=si)
        return Quantity(si=si)

    def __rtruediv__(self, other):
        from .unitless import Unitless

        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = np.divide(other.si, self.si)
        if isinstance(other, Unitless):
            return type(self)(si=si)
        if type(other) is type(self):
            return Unitless(si=si)
        return Quantity(si=si)

    def __pow__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = self.si**other.si
        return Quantity(si=si)

    def __rpow__(self, other):
        if not isinstance(other, Quantity):
            other = Quantity(si=other)
        si = other.si**self.si
        return Quantity(si=si)

    def __neg__(self):
        return type(self)(si=-self.si)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        from .unitless import Unitless
        if ufunc == np.power:
            base, exp = inputs
            if isinstance(base, Quantity) and isinstance(exp, (int, float, np.ndarray)):
                return Quantity(si=np.power(base.si, exp))
            elif isinstance(exp, Quantity) and isinstance(
                base, (int, float, np.ndarray)
            ):
                return Quantity(si=np.power(base, exp.si))
            elif isinstance(exp, Quantity) and isinstance(base, Quantity):
                return Quantity(si=np.power(base.si, exp.si))
            else:
                raise TypeError("Invalid types for np.power with Quantity.")
        elif ufunc == np.add and method == "reduce":
            si = ufunc.reduce(inputs[0].si, **kwargs)
            return type(self)(si=si)
        elif ufunc == np.multiply and method == "reduce":
            si = ufunc.reduce(inputs[0].si, **kwargs)
            return Quantity(si=si)
        elif ufunc == np.exp:
            si = ufunc(inputs[0].si)
            if isinstance(inputs[0], Unitless):
                return Unitless(si=si)
            return Quantity(si=si)
        elif ufunc == np.log:
            si = ufunc(inputs[0].si)
            if isinstance(inputs[0], Unitless):
                return Unitless(si=si)
            return Quantity(si=si)
        return NotImplemented
