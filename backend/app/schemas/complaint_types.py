from pydantic import BaseModel
from typing import List

class Urgency(BaseModel):
    score:int

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
    id: str
    group: int
    coordinates: List[float]
    sources: List[Source]
    location: str
    summary: str
    solution_outline: str

class ProposalInput(BaseModel):
    location:str
    coordinates:List[float]
    summary:str
    solution_outline:str