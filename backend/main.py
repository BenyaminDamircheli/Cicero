from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from geopy.distance import distance
from fastapi import Body
import json
from itertools import groupby

from utils.data_scraping.data_processor import Processor
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = "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"
client = OpenAI(api_key=API_KEY)

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

class Source(BaseModel):
    title:str
    url:str
    body:str

class GroupedComplaint(BaseModel):
    id:str
    coordinates:List[float]
    sources:List[Source]

class Urgency(BaseModel):
    score:int
    explanation:str

class Summary(BaseModel):
    title:str
    summary:str
    urgency:Urgency
    solutions:str

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


def generate_complaint_summary(complaint: GroupedComplaint):
    sources = complaint.sources
    result = ""
    for source in sources:
        result += f"Title: {source.title}\nBody: {source.body[:1000]}\n\n ----------------------\n\n"

    prompt = f"""
    Analyze the following complaints:
    {result}

    1. Provide a short title that best describes the complaints.
    2. Provide a short summary of the complaints (100 words max).
    3. Assign an urgency score from 1-5 and explain why (50 words max).
    4. Propose a potential solution(s) to address the complaints, keep this in paragraph form, no lists (100 words max).
    """

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant analyzing citizen complaints and proposing solutions THAT ONLY RESPONDS IN JSON FORMAT."},
            {"role": "user", "content": prompt}
        ],
        response_format=Summary
        )
    except Exception as e:
        print("Error generating complaint summary: ", e)
        return {"error": "Failed to generate complaint summary"}

    content = response.choices[0].message.content
    loaded = json.loads(content)
    print(loaded)
    return loaded


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
