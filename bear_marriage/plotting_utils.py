import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from .data import ColoredPoint


def plot_points(points: list[ColoredPoint]) -> Figure:
    x_coords = [point.x for point in points]
    y_coords = [point.y for point in points]
    colors = [point.black for point in points]
    plt.scatter(x_coords, y_coords, c=colors)
    return plt.gcf()


def plot_polygon(points: list[ColoredPoint]) -> Figure:
    points = points + [points[0]]
    x_coords = [point.x for point in points]
    y_coords = [point.y for point in points]
    plt.plot(x_coords, y_coords)
    return plt.gcf()


def plot_pairs(pairs: list[tuple[ColoredPoint, ColoredPoint]]) -> go.Figure:
    fig = make_subplots()

    for a_point, b_point in pairs:
        data = ([a_point.x, b_point.x], [a_point.y, b_point.y])
        fig.add_trace(go.Scatter(x=data[0], y=data[1], mode='lines+markers',
                                 marker=dict(color=[a_point.black, b_point.black])))

    return fig
