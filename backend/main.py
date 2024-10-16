from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from geopy.distance import distance
from fastapi import Body
import json
from itertools import groupby
from utils.types import GroupedComplaint, Source
from utils.data_scraping.data_processor import Processor
from openai import OpenAI
from dotenv import load_dotenv
import os
from utils.complaint_summary.complaint_summary import generate_complaint_summary
load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = Processor()
SessionLocal = processor.SessionLocal

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
        return grouped_complaints
    finally:
        db.close()

@app.post("/api/complaints/summary")
async def get_complaint_summary(complaint: GroupedComplaint):
    print("Generating complaint summary")
    summary = generate_complaint_summary(complaint)
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
