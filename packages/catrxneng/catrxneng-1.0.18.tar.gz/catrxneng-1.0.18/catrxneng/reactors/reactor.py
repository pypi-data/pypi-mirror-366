import plotly.graph_objects as go, numpy as np


class Reactor:

    def __init__(self):
        self.conditions = {"ghsv": None, "T": None, "p0": None, "mcat": None}

    def check_components(self):
        if self.conditions["p0"].size != len(self.rate_model.components):
            raise ValueError(
                "Number of components for reactor and rate model do not match."
            )

    def plot(self, x, y, names, modes, xlabel, ylabel, title=None):
        fig = go.Figure()
        for i in range(len(y)):
            trace = go.Scatter(x=x[i], y=[i], mode=modes[i], name=names[i])
            fig.add_trace(trace)
        fig.update_layout(
            title=dict(text=f"<b>{title}</b>", x=0.5),
            xaxis_title=f"<b>{xlabel}</b>",
            yaxis_title=f"<b>{ylabel}</b>",
            width=800,
        )
        fig.show()
