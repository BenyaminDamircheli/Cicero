from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
from schemas.complaint_types import GroupedComplaint, Source
from services.group_complaints import group_complaints
from services.complaint_summary import generate_complaint_summary
from services.data_saver import Complaint, SessionLocal, save_complaint_summary
from models.models import Base, engine

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:6543"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# makes sure tables are created if they don't exist.
# doesnt change existing tables.
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Complaints API"}

@app.get("/api/complaints", response_model=List[GroupedComplaint])
async def get_complaints():
    db = SessionLocal()
    try:
        print("Getting complaints")
        complaints = db.query(Complaint).all()
        grouped_complaints = group_complaints(complaints)
        return grouped_complaints
    finally:
        db.close()

@app.post("/api/complaints/summary")
async def get_complaint_summary(complaint: GroupedComplaint):
    print("Generating complaint summary")
    summary = generate_complaint_summary(complaint)
    print(summary)
    print("Saving complaint summary")
    save_complaint_summary(complaint, summary)
    print("Complaint summary saved")
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
