from io import BytesIO

from fastapi import FastAPI
from fastapi import UploadFile
from pydantic import BaseModel

from .data import read_points, ColoredPoint
from .find_pairs import connect_points


app = FastAPI()


@app.post("/send_file/")
async def send_file(file: UploadFile) -> list[ColoredPoint]:
    contents = await file.read()
    points = read_points(BytesIO(contents))
    return points


@app.post("/get_pairs/")
async def get_pairs(points: list[ColoredPoint]) -> list[tuple[ColoredPoint, ColoredPoint]]:
    pairs = connect_points(points)
    return pairs