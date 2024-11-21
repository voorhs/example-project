from io import BytesIO
from dataclasses import asdict

import plotly.graph_objects as go
import requests

from .data import ColoredPoint

BASE_URL = "http://localhost:8000"

def read_points(file: BytesIO) -> list[ColoredPoint]:
    response = requests.post(
        f"{BASE_URL}/send_file",
        files={"file": file.getvalue()}
    )
    raw_data = response.json()
    return [ColoredPoint(**record) for record in raw_data]

def connect_points(
    points: list[ColoredPoint],
) -> list[tuple[ColoredPoint, ColoredPoint]]:
    response = requests.post(
        f"{BASE_URL}/get_pairs",
        json=[p.model_dump() for p in points]
    )
    if response.status_code != 200:
        return response
    response.raise_for_status()
    raw_data = response.json()
    return [(ColoredPoint(**record_1), ColoredPoint(**record_2)) for record_1, record_2 in raw_data]
