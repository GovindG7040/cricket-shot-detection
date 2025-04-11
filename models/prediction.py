# models/prediction.py

from pydantic import BaseModel
from typing import List

class KeypointsInput(BaseModel):
    keypoints: List[float]

class PredictionOutput(BaseModel):
    predicted_shot: str
