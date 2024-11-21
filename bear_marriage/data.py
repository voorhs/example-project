from dataclasses import dataclass

import numpy as np
import numpy.typing as npt


@dataclass
class ColoredPoint:
    x: float
    y: float
    black: bool

    def __lt__(self, other: "ColoredPoint") -> bool:
        return (self.x, self.y) < (other.x, other.y)


def color_points(points: npt.NDArray[np.float32], black: bool):
    return [ColoredPoint(x, y, black) for x, y in points.tolist()]


def sample_data(n: int, seed: int | None = 0) -> list[ColoredPoint]:
    if seed is not None:
        np.random.seed(seed)
    all_points = np.random.uniform(-1, 1, size=(2 * n, 2))
    blacks, whites = all_points[:n], all_points[n:]
    return color_points(blacks, black=True) + color_points(whites, black=False)
