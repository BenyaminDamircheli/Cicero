from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from geopy.distance import distance

from itertools import groupby

from utils.data_scraping.data_processor import Processor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = Processor()
SessionLocal = processor.SessionLocal

class Source(BaseModel):
    title:str
    url:str
    body:str

class GroupedComplaint(BaseModel):
    id:str
    coordinates:List[float]
    sources:List[Source]

def group_complaints(complaints):
    def group_key(complaint):
        return complaint.group

    def merge_complaints(group):
        with_coords = [c for c in group if c.coordinates]
        no_coords = [c for c in group if not c.coordinates]

        result = []
        for complaint in with_coords:
            nearby = [c for c in with_coords if c != complaint]

            all_sources = [Source(title=c.title, body=c.body, url=c.url) for c in nearby + no_coords + [complaint]]
            sources = all_sources[:5]

            result.append(
                GroupedComplaint(
                    id = f'{complaint.group}_{complaint.id}',
                    coordinates= complaint.coordinates[0], 
                    sources = sources
                )
            )

        return result
        
    sorted_complaints = sorted(complaints, key=group_key)
    grouped = groupby(sorted_complaints, key=group_key)

    return [
        complaint 
        for _,group in grouped
        for complaint in merge_complaints(list(group))
        ]

@app.get("/")
async def root():
    return {"message": "Welcome to the Complaints API"}

@app.get("/api/complaints", response_model=List[GroupedComplaint])
async def get_complaints():
    db = SessionLocal()
    try:
        print("Getting complaints")
        complaints = db.query(processor.Complaint).all()
        grouped_complaints = group_complaints(complaints)
        print(grouped_complaints[:5])
        return grouped_complaints
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
