from fastapi import FastAPI, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from fastapi import HTTPException
from typing import List
from dotenv import load_dotenv
from schemas.complaint_types import GroupedComplaint, Source, ProposalInput
from services.group_complaints import group_complaints
from services.complaint_summary import generate_complaint_summary
from services.data_saver import Complaint, SessionLocal, save_complaint_summary
from models.models import Base, engine
from websocket_manager import manager
from agents.research_supervisor import ProposalSupervisor, State
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:6543"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ensures tables are created if they don't exist
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to the Complaints API"}

# Websocket for testing
@app.websocket("/ws/test/{client_id}")
async def test_websocket(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "connected":
                    print("WebSocket connected")
            except WebSocketDisconnect:
                manager.disconnect(client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)

# websocket for live research updates
@app.websocket("/ws/proposal/{client_id}")
async def proposal_websocket(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                if data == "connected":
                    print("WebSocket connected")
            except WebSocketDisconnect:
                manager.disconnect(client_id)
                break
    except WebSocketDisconnect:
        manager.disconnect(client_id)

@app.post("/api/proposals/generate/{client_id}")
async def generate_proposal(complaint: ProposalInput, client_id: str):
    supervisor = ProposalSupervisor(client_id)
    graph = supervisor.create_graph()
    
    state = State(
        location=complaint.location,
        coordinates=complaint.coordinates,
        summary=complaint.summary,
        solution_outline=complaint.solution_outline,
        messages=[],
        next_action="",
        zoning_info={},
        pois=[],
        ranked_pois=[],
        zoning_policies=[],
        research_results=[],
        research_plan={},
        proposal={},
        research_feedback=""
    )
    print("Invoking graph")
    result = await graph.ainvoke(state)
    
    return result

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
    summary = generate_complaint_summary(complaint)
    save_complaint_summary(complaint, summary)
    return summary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)