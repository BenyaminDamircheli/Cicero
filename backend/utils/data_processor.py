# Standard library imports
import os
from urllib.parse import quote_plus

import nltk
import numpy as np
import spacy
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, JSON, ARRAY, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sklearn.cluster import DBSCAN
from geopy.geocoders import Nominatim
# from geopy.distance import geodesic ---- Maybe needed later
from tqdm import tqdm

load_dotenv()


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
    coordinates = Column(ARRAY(Float))
    summary = Column(String)
    topics = Column(ARRAY(Float))
    group = Column(Integer)

Base.metadata.create_all(bind=engine)

# NLP setup
nlp = spacy.load("en_core_web_trf")
nltk.download('vader_lexicon')
nltk.download('stopwords')
nltk.download('punkt')
sia = SentimentIntensityAnalyzer()
sentence_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1', trust_remote_code=True)
summarizer = LsaSummarizer()
stopwords = set(stopwords.words("english"))

geolocator = Nominatim(user_agent="myapp")

def get_coordinates(location):
    try:
        location = geolocator.geocode(f"{location}, Toronto, Ontario, Canada")
        if location:
            return (location.latitude, location.longitude)
    except:
        pass
    return None

def preprocess_text(text):
    tokens = word_tokenize(text)
    return [token for token in tokens if token.isalnum() and token not in stopwords]

def summarize_text(text, sentences_count=4):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summary = summarizer(parser.document, sentences_count)
    return " ".join([str(sentence) for sentence in summary])

def process_text(text):
    if not isinstance(text, str):
        text = str(text)  

    doc = nlp(text)
    
    sentiment = sia.polarity_scores(text)
    is_complaint = sentiment['compound'] < -0.05  # play with this a bit
    
    locations = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "FAC"] and ent.text.lower() != "toronto" and ent.text.lower() != "ontario" and ent.text.lower() != "canada"]
    embeddings = sentence_model.encode(text)
    summary = summarize_text(text)
    
    coordinates = [get_coordinates(loc) for loc in locations]
    coordinates = [coord for coord in coordinates if coord is not None]
    
    return {
        'is_complaint': is_complaint,
        'sentiment': sentiment,
        'locations': locations,
        'coordinates': coordinates,
        'summary': summary,
        'embeddings': embeddings
    }


def group_complaints(processed_data, similarity_threshold=0.67):
    groups = []
    
    for item in tqdm(processed_data, desc="Grouping complaints"):

        added_to_group = False
        for group in groups:
            if cosine_similarity([item['embeddings']], [group[0]['embeddings']])[0][0] >= similarity_threshold:
                group.append(item)
                added_to_group = True
                break
        
        #if this item doesn't fit into a group, make a new one.
        if not added_to_group:
            groups.append([item])
    
    # Assign group numbers
    for i, group in enumerate(groups):
        for item in group:
            item['group'] = i
    
    return [item for group in groups for item in group]

def process_and_save_data(data):
    processed_data = []
    db = SessionLocal()
    try:
        for item in tqdm(data, desc="Processing data"):
            full_text = f"{item['title']} {item['body']}"
            analysis = process_text(full_text)
            
            processed_item = {
                'title': item['title'],
                'body': item['body'],
                'url': item['url'],
                'created_at': item['created'],
                'is_complaint': analysis['is_complaint'],
                'sentiment': analysis['sentiment'],
                'locations': analysis['locations'],
                'coordinates': analysis['coordinates'],
                'summary': analysis['summary'],
                'embeddings': analysis['embeddings']
            }
            processed_data.append(processed_item)
        
        # Group complaints
        grouped_data = group_complaints(processed_data)
        
        for item in tqdm(grouped_data, desc="Saving data"):
            complaint = Complaint(
                title=item['title'],
                body=item['body'],
                url=item['url'],
                created_at=item['created_at'],
                is_complaint=item['is_complaint'],
                locations=item['locations'],
                coordinates=item['coordinates'],
                summary=item['summary'],
                topics=item['embeddings'].tolist(),  # Store embeddings as topics
                group=item['group']
            )
            db.add(complaint)
        db.commit()
    finally:
        db.close()
    
    return grouped_data

def get_complaints():
    db = SessionLocal()
    try:
        return db.query(Complaint).all()
    finally:
        db.close()


