from pydantic import BaseModel
from typing import List

class Urgency(BaseModel):
    score:int
    explanation:str

class Summary(BaseModel):
    title:str
    summary:str
    urgency:Urgency
    solutions:str

class Source(BaseModel):
    title:str
    url:str
    body:str

class GroupedComplaint(BaseModel):
    id:str
    coordinates:List[float]
    sources:List[Source]