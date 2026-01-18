from pydantic import BaseModel
from typing import List

class Sensor_data(BaseModel):
    cycle:int
    op1: float
    op2: float
    op3: float
    s3:float
    s4:float
    s9:float
    s11:float
    s12:float
    s13:float
    s14:float
    s15:float
    s20:float

class live_data(BaseModel):
    sensor_data: List[Sensor_data]