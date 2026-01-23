from pydantic import BaseModel
from datetime import date
from typing import List


class IntakeRequest(BaseModel):
    name: str
    birthdate: date
    answers: List[int]
