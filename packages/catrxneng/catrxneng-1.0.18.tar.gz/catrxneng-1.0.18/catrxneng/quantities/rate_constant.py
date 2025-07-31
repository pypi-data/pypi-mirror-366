from .quantity import Quantity


class RateConstant(Quantity):
    def __init__(self, order=None, **kwargs):
        self.order = order
        super().__init__(**kwargs)

    @property
    def molskgcatPa(self):
        return self.si

    @molskgcatPa.setter
    def molskgcat(self, value):
        from ..utils import to_float
        self.si = to_float(value)

    @property
    def molhgcatbar(self):
        return self.si * 3600 / 1000 * (100000**self.order)

    @molhgcatbar.setter
    def molhgcatbar(self, value):
        from ..utils import to_float
        self.si = to_float(value / 3600 * 1000 / (100000**self.order))
