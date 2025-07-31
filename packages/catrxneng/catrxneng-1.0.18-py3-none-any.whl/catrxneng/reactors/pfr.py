import numpy as np
from scipy.integrate import solve_ivp

from ..quantities import *
from .reactor import Reactor


class PFR(Reactor):
    def __init__(self, conditions, rate_model):
        super().__init__()
        self.conditions = conditions
        self.Ft0 = self.conditions["ghsv"] * self.conditions["mcat"]
        self.conditions["P0"] = np.sum(self.conditions["p0"])
        self.y0 = self.conditions["p0"] / self.conditions["P0"]
        self.F0 = self.y0 * self.Ft0
        self.rate_model = rate_model
        self.check_components()

    def dFdw(self, w, F):
        F = MolarFlowRate(molh=F)
        Ft = np.sum(F)
        y = F / Ft
        p = y * self.conditions["P0"]
        T = self.conditions["T"]
        return np.array([rate(T, p).molhgcat for rate in self.rate_model.rate])

    def solve(self):
        w_span = (0, self.conditions["mcat"].g)
        w_eval = np.linspace(0, self.conditions["mcat"].g, 1000)
        solution = solve_ivp(self.dFdw, w_span, self.F0.molh, t_eval=w_eval)
        self.w = Mass(g=solution.t)
        self.F = MolarFlowRate(molh=solution.y)
        self.Ft = np.sum(self.F, axis=0)
        self.y = self.F / self.Ft
        self.conv = (self.F0[0] - self.F[0]) / self.F0[0]
        self.inv_ghsv = InvGHSV(si=self.w.si / self.Ft0.si)
        self.ghsv = GHSV(si=1/self.inv_ghsv.si)
        vol_flow_rate = self.Ft0 * R * self.conditions["T"] / self.conditions["P0"]
        self.v = VolumetricFlowRate(si=vol_flow_rate.si)
        self.tau_mod = self.w.g / self.v.mLs
    
    def rate(self):
        p = self.y * self.conditions["P0"]
        rates = []
        for ri in self.rate_model.rate:
            rates.append(ri(self.conditions["T"], p))
        return rates

