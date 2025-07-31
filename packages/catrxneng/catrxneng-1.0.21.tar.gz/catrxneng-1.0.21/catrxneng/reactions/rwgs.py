import numpy as np

from .reaction import Reaction
from ..quantities import *
from ..species import *


class RWGS(Reaction):
    def __init__(self, T):
        # self.components = {
        #     "CO2": CO2(T=T, stoich_coeff=-1),
        #     "H2": H2(T=T, stoich_coeff=-1),
        #     "CO": CO(T=T, stoich_coeff=1),
        #     "H2O": H2O(T=T, stoich_coeff=1),
        #     "inert": Ar(T=T, stoich_coeff=0)
        # }
        self.components = (CO2(T), H2(T), CO(T), H2O(T), Ar(T))
        self.stoich_coeff = Unitless(si=[-1.0, -1.0, 1.0, 1.0, 0.0])
        super().__init__(T)
