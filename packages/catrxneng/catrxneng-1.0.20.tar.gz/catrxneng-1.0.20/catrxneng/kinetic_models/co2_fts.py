import numpy as np
from catrxneng.utils import k
from catrxneng.reactions import RWGS
from catrxneng.quantities import *


class Brubach2022:
    def __init__(self):
        self.components = ("CO2", "H2", "CO", "H2O", "Ar")
        self.Ea_rwgs = Energy(kJmol=115)
        self.Ea_ft = Energy(kJmol=67.8)
        self.a_rwgs = Unitless(si=16.3)
        self.a_ft = Unitless(si=9.07)
        self.b_ft = InversePressure(inv_bar=2.44)
        self.kref_rwgs = RateConstant(order=1.5, molhgcatbar=8.13e-2)
        self.kref_ft = RateConstant(order=2, molhgcatbar=6.39e-2)
        self.Tref = Temperature(C=300)
        self.construct_rate_eqn()

    def k_rwgs(self, T):
        return k(T=T, Ea=self.Ea_rwgs, kref=self.kref_rwgs, Tref=self.Tref)

    def k_ft(self, T):
        return k(T=T, Ea=self.Ea_ft, kref=self.kref_ft, Tref=self.Tref)

    def r_rwgs(self, T, p):
        fwd = p[0] * p[1] ** 0.5
        rev = p[2] * p[3] / (RWGS(T).Keq * p[1] ** 0.5)
        num = self.k_rwgs(T) * (fwd - rev)
        denom = (1 + self.a_rwgs * p[3] / p[1]) ** 2
        rate = num / denom
        return ReactionRate(si=rate.si)

    def r_ft(self, T, p):
        num = self.k_ft(T) * p[1] * p[2]
        denom = (1 + self.a_ft * p[3] / p[1] + self.b_ft * p[2]) ** 2
        rate = num / denom
        return ReactionRate(si=rate.si)

    def construct_rate_eqn(self):
        self.rate = np.array(
            [
                lambda T, p: -self.r_rwgs(T, p),  # CO2
                lambda T, p: -self.r_rwgs(T, p) - 2 * self.r_ft(T, p),  # H2
                lambda T, p: self.r_rwgs(T, p) - self.r_ft(T, p),  # CO
                lambda T, p: self.r_rwgs(T, p) + self.r_ft(T, p),  # H2O
                lambda T, p: ReactionRate(si=0),  # Ar 
            ]
        )
