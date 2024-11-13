# Cicero

Cicero is a proof of concept for how LLM agents can be used by governments and urban planners to turn citizen complaints into actionable proposals. 

Check it out in action [here](https://www.youtube.com/watch?v=NLCgRhxzia4)

Before building the agents, I first had to scrape 10k+ posts from online forums, government polls and online news articles. Then I used NLP techniques to extract relevant information such as location, sentiment and what issues are related to eachother in order to aggregate a list of 1k+ issues in Toronto.

I visualized this data using a mapbox and a sidebar that shows the complaint details, sources and improvements.

Langgraph was used to build the agent graph that coordinates multiple specialized agents:

- **POI Finder**: Identifies relevant points of interest near complaint locations
- **Zoning Checker**: Verifies zoning regulations and bylaws
- **Policy Researcher**: Analyzes relevant municipal policies
- **Web Researcher**: Gathers data from trusted sources about similar issues/solutions
- **POI Ranker**: Ranks potential locations based on suitability
- **Proposal Writer**: Generates formal municipal proposals

The agents work together through a supervisor that manages the research and writing workflow.

## Tech Stack

- **Frontend**: Next.js, TailwindCSS, Framer Motion
- **Backend**: FastAPI, LangGraph, SQLAlchemy
- **Database**: PostgreSQL (Supabase)
- **ML/NLP**: spaCy, NLTK, sentence transformers(for embeddings which cluster complaints)
- **Data Sources**: Reddit API, Toronto Open Data, Web Scraping


## Installation

1. Clone the repository
2. Install frontend dependencies:

```bash
cd cicero
npm install
```

3. Install backend dependencies:

```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables:
- Create `.env` in backend directory with:
  - Database credentials
  - OpenAI API key
  - Reddit API credentials
  - Tavily API key

5. Run the development servers:

```bash
npm run dev # frontend
uvicorn app.main:app --reload # backend
```

You will have to run the scraping script to populate the database (which you should make with supabase or another postgres database). This will also process the data and group it which can take a while (on my M2 air it took ~20-30 minutes). From there you should be able to run the frontend and backend and have a working version of Cicero. This does unfortunately take a lot of resources so I would recommend running this only on beefy machines like the apple silicon macs.

## Final Thoughts

This project taught me a lot about webscraping, data processing with NLP libraries and how to coordinate LLM agents with LangGraph and LangChain. I'm sure there are many ways this project could be improved, especially with the agent architecture (I think the design is overly complex) but I'm happy with how it turned out and I learned a lot in the process.