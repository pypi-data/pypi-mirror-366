import numpy as np, pandas as pd, os, json
from .time import Time


def k(T, Ea, k0=None, kref=None, Tref=None):
    from ..quantities import R, RateConstant

    if kref and Tref:
        k0 = kref / (np.exp(-Ea / (R * Tref)))
        k0 = RateConstant(si=k0.si, order=kref.order)

    k = k0 * np.exp(-Ea / (R * T))
    return RateConstant(si=k.si, order=k0.order)


def to_float(value):
    if isinstance(value, np.ndarray):
        return value.astype(float)
    if isinstance(value, int):
        return float(value)
    return value


def plot_info_box(text):
    annotations = [
        dict(
            x=0.5,
            y=-0.32,
            xref="paper",
            yref="paper",
            text=text,
            showarrow=False,
            font=dict(size=12, style="italic", weight="bold"),
        )
    ]
    return annotations


def get_conf(conf_name):
    conf_name = conf_name + ".conf"
    conf_dir = os.path.join(os.path.dirname(__file__), "..", "..", "confs")
    file_path = os.path.join(conf_dir, conf_name)
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Configuration file '{conf_name}' not found in 'conf' folder."
        )
    with open(file_path, "r") as file:
        return json.load(file)
