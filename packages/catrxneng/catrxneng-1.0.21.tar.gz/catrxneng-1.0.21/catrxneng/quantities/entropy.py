from .quantity import Quantity
from .energy import Energy
from .temperature import Temperature
from catrxneng.utils import *


class Entropy(Quantity):

    @property
    def JmolK(self):
        return self.si

    @JmolK.setter
    def JmolK(self, value):
        self.si = to_float(value)

    @property
    def kJmolK(self):
        return self.si / 1000

    @kJmolK.setter
    def kJmolK(self, value):
        self.si = to_float(value * 1000)

    def __mul__(self, other):
        if isinstance(other, Temperature):
            si = self.si * other.si
            return Energy(si=si)
        else:
            return super().__mul__(other)

    def __rmul__(self, other):
        if isinstance(other, Temperature):
            si = other.si * self.si
            return Energy(si=si)
        else:
            return super().__rmul__(other)
