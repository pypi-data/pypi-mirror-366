import numpy as np
from scipy.optimize import minimize

from catrxneng.quantities import *


class Reaction:
    def __init__(self, T):
        self.T = T
        self.fug_coeff = Unitless(si=np.ones(len(self.components)))
        self.update()

    @property
    def comp_list(self):
        return (comp.__class__.__name__ for comp in self.components)

    def update(self):
        for comp in self.components:
            comp.T = self.T
        self.Hf = Energy(si=[comp.Hf.si for comp in self.components])
        self.Sf = Entropy(si=[comp.Sf.si for comp in self.components])
        self.dHr = np.sum(self.Hf * self.stoich_coeff)
        self.dSr = np.sum(self.Sf * self.stoich_coeff)
        self.dGr = self.dHr - self.dSr * self.T
        self.Keq = np.exp(-self.dGr / (R * self.T))

    def check_components(self, p0):
        if p0.size != len(self.components):
            raise ValueError(
                "Number of components for reactor and rate model do not match."
            )

    def eq_conv(self, p0):
        self.check_components(p0)
        P = np.sum(p0)
        initial_total_mol = 100
        initial_molfrac = p0 / P
        initial_mol = initial_molfrac * initial_total_mol
        std_state_fugacity = Pressure(atm=np.ones(len(self.components)))

        def objective(extent):

            extent = Quantity(si=extent)
            mol = initial_mol + extent * self.stoich_coeff
            total_mol = np.sum(mol)
            molfrac = mol / total_mol
            fugacity = molfrac * self.fug_coeff * P
            activity = fugacity / std_state_fugacity
            Ka = np.prod(activity**self.stoich_coeff)
            # Kx = np.prod(molfrac**self.stoich_coeff)
            # Kphi = np.prod(self.fug_coeff**self.stoich_coeff)
            # Kp = np.prod(P**self.stoich_coeff)
            # Kf0 = np.prod(std_state_fugacity**self.stoich_coeff)
            return ((Ka - self.Keq) ** 2).si * 1e5

        adj_init_mol_reactants = np.array(
            [
                mol / stoich_coeff
                for mol, stoich_coeff in zip(initial_mol.si, self.stoich_coeff.si)
                if stoich_coeff < 0
            ]
        )
        bounds = [(0.00001, np.min(-adj_init_mol_reactants) * 0.99999)]
        initial_guess = -0.5 * initial_mol.si[0] / self.stoich_coeff.si[0]
        result = minimize(
            objective,
            initial_guess,
            bounds=bounds,
            options={"ftol": 1e-10},
        )
        if result.success:
            extent = result.x[0]
            conv = -self.stoich_coeff.si[0] * extent / initial_mol.si[0]
            return Unitless(si=conv)
        else:
            raise ValueError("Optimization failed: " + result.message)
