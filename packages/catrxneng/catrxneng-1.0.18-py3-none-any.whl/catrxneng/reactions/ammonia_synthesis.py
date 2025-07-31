from .reaction import Reaction
from .. import species


class AmmoniaSynthesis(Reaction):
    def __init__(self, T):
        self.components = {
            "N2": species.N2(T=T, stoich_coeff=-0.5),
            "H2": species.H2(T=T, stoich_coeff=-1.5),
            "NH3": species.NH3(T=T, stoich_coeff=1),
            "inert": species.Ar(T=T, stoich_coeff=0),
        }
        super().__init__(T)
