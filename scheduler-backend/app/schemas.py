from pydantic import BaseModel
from datetime import datetime




class EventCreate(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime

class EventUpdateStatus(BaseModel):
    status: str


class SwapCreate(BaseModel):
    my_slot_id: int
    their_slot_id: int

class SwapResponse(BaseModel):
    accept: bool
