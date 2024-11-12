import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from backend.app.agents.research_supervisor import ProposalSupervisor, State
import asyncio

async def test_supervisor():
    # Create test state
    test_state = State(
        location="Niagara",
        coordinates=[43.6532, -79.3832],
        summary="The complaint highlights a noticeable increase in homelessness and encampments in downtown areas and parks. The prevalence of tents signifies a worsening crisis, impacting community perceptions and raising concerns about the well-being of vulnerable populations in communities like Niagara.",
        solution_outline="Implement an immediate emergency response program to provide shelters, mental health services, and job training for the homeless. Collaborative efforts with local charities and organizations can facilitate long-term housing solutions and enhance community support.",
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

    # Initialize supervisor
    supervisor = ProposalSupervisor()
    
    # Create graph
    graph = supervisor.create_graph()
    
    # Run graph with test state
    result = await graph.ainvoke(test_state)
    print("Final State:", result)

if __name__ == "__main__":
    asyncio.run(test_supervisor()) 