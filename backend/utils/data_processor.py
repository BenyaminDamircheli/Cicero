from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
import os
from dotenv import load_dotenv
import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
import numpy as np
from urllib.parse import quote_plus


load_dotenv()

# Database setup
db_user = os.environ.get("user", "postgres.zeaafwuqllrqcvytkhaf")
db_password = os.environ.get("password", "Benyamin2024!")
db_host = os.environ.get("host", "aws-0-us-west-1.pooler.supabase.com")
db_port = os.environ.get("port", "6543")
db_name = os.environ.get("dbname", "postgres")

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql+psycopg2://{quote_plus(db_user)}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name}?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    url = Column(String)
    created_at = Column(Float)
    is_complaint = Column(Boolean)
    locations = Column(ARRAY(String))
    cluster = Column(Integer)

Base.metadata.create_all(bind=engine)

nlp = spacy.load("en_core_web_sm")
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()
sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

def process_text(text):
    # Perform NLP analysis
    doc = nlp(text)
    
    # Identify complaints using sentiment analysis
    sentiment = sia.polarity_scores(text)
    is_complaint = sentiment['compound'] < -0.05  # Adjust this threshold as needed
    
    # Extract locations
    locations = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC", "FAC"]]
    
    # Generate embedding
    embedding = sentence_model.encode(text).tolist()
    
    return {
        'is_complaint': is_complaint,
        'sentiment': sentiment,
        'locations': locations,
        'embedding': embedding
    }


def process_and_save_data(data):
    processed_data = []
    db = SessionLocal()
    try:
        for item in data:
            full_text = f"{item['title']} {item['body']}"
            analysis = process_text(full_text)
            
            processed_item = {
                'title': item['title'],
                'body': item['body'],
                'url': item['url'],
                'created': item['created'],
                'is_complaint': analysis['is_complaint'],
                'locations': analysis['locations'],
                'embedding': analysis['embedding']
            }
            processed_data.append(processed_item)
            
            complaint = Complaint(
                title=item['title'],
                body=item['body'],
                url=item['url'],
                created_at=item['created'],
                is_complaint=analysis['is_complaint'],
                locations=analysis['locations'],
            )
            db.add(complaint)
        db.commit()
    finally:
        db.close()
    return processed_data

def get_complaints():
    db = SessionLocal()
    try:
        return db.query(Complaint).all()
    finally:
        db.close()



text = """
I know that city council voted to move forward last week with its plan to rename Yonge-Dundas Square to Sankofa Square so this is mostly a toothless rant, especially on a beautiful weekend but I know this sub is strict on the weekdays.

Did you know that we are six months away from the Accessibility for Ontarians with Disabilities Act's aim to make the province fully accessible by 2025? I moved here from the U.S. and am old enough to have witnessed the impact of the Americans with Disabilities Act and that was passed in 1990, Ontario's didn't pass until 2005! TTC announcements are useless and inaudible to even those who aren't hard of hearing and GO Trains don't even have any signage for someone who can't hear an announcement and these are just two small examples that would improve everyone's life.

Coun. Amber Morley said, "Black people are Canadians, too. Black people pay taxpayer dollars, too. So God forbid we put a couple of dollars towards a truth and reconciliation to hold space for community members who have long been disregarded and discarded in violent and traumatic ways."

All of this can be said about Canadians with disabilities except guess what? Not a single one of us could wake up tomorrow a different race, but any one of us could wake up with a disability.   

Yes, the obvious choice is Terry Fox and I can easily picture a statue that tourists would want to visit and rub his running shoe for good luck.  I actually first learned about Terry Fox when I came here as a tourist and visited the Bata Shoe Museum.  Imagine tourists actually learning something about an impactful Canadian instead of a word from a completely different country.

This would also put some heat on the province/city to do something useful about the 2025 deadline.  I want to note that I do not have a disability but one of the biggest culture shocks when I moved here over 15 years ago was the lack of accessibility in Toronto.  I only learned how little ODSP pays during covid when I found out it was less than CERB.  It's not a competition, but this is the truth and reconciliation I believe our community needs.
"""

print(process_text(text))