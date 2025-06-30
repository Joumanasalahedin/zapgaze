from pydantic import BaseModel
from typing import Optional


class EyeData(BaseModel):
    x: Optional[float]
    y: Optional[float]
    pupil_size: Optional[float] = None


class AcquisitionData(BaseModel):
    session_uid: str
    timestamp: float
    left_eye: EyeData
    right_eye: EyeData
    ear: Optional[float] = None
    blink: Optional[bool] = None
