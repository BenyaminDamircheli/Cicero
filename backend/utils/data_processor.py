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
from tqdm import tqdm

class Processor:
    def __init__(self):
        load_dotenv()

        self.db_user = os.environ.get("user", "postgres.zeaafwuqllrqcvytkhaf")
        self.db_password = os.environ.get("password", "Benyamin2024!")
        self.db_host = os.environ.get("host", "aws-0-us-west-1.pooler.supabase.com")
        self.db_port = os.environ.get("port", "6543")
        self.db_name = os.environ.get("dbname", "postgres")

        self.DATABASE_URL = f"postgresql+psycopg2://{quote_plus(self.db_user)}:{quote_plus(self.db_password)}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode=require"

        self.engine = create_engine(self.DATABASE_URL, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        self.Base = declarative_base()

        class Complaint(self.Base):
            __tablename__ = "complaints1"

            id = Column(Integer, primary_key=True, index=True)
            title = Column(String)
            body = Column(String)
            url = Column(String)
            created_at = Column(Float)
            is_complaint = Column(Boolean)
            locations = Column(ARRAY(String))
            coordinates = Column(ARRAY(Float))
            topics = Column(ARRAY(Float))
            group = Column(Integer)

        self.Complaint = Complaint
        self.Base.metadata.create_all(bind=self.engine)

        self.nlp_reddit = spacy.load("en_core_web_trf")
        self.nlp_website = spacy.load("en_core_web_sm")

        nltk.download('vader_lexicon')
        nltk.download('stopwords')
        nltk.download('punkt')
        self.sia = SentimentIntensityAnalyzer()
        self.sentence_model = SentenceTransformer('nomic-ai/nomic-embed-text-v1', trust_remote_code=True)
        self.summarizer = LsaSummarizer()
        self.stopwords = set(stopwords.words("english"))

        self.geolocator = Nominatim(user_agent="myapp")

    def get_coordinates(self, location):
        try:
            location = self.geolocator.geocode(f"{location}, Toronto, Ontario, Canada")
            if location:
                return (location.latitude, location.longitude)
        except:
            pass
        return None

    def preprocess_text(self, text):
        tokens = word_tokenize(text)
        return [token for token in tokens if token.isalnum() and token not in self.stopwords]

    def process_text(self, text, nlp):
        if not isinstance(text, str):
            text = str(text)  

        doc = nlp(text)
        
        sentiment = self.sia.polarity_scores(text)
        is_complaint = sentiment['compound'] < -0.05  # play with this a bit
        
        locations = [ent.text for ent in doc.ents if ent.label_ in ["LOC", "FAC"] and ent.text.lower() not in ["toronto", "ontario", "canada"]]
        embeddings = self.sentence_model.encode(text)
        
        coordinates = [self.get_coordinates(loc) for loc in locations]
        coordinates = [coord for coord in coordinates if coord is not None]
        
        return {
            'is_complaint': is_complaint,
            'sentiment': sentiment,
            'locations': locations,
            'coordinates': coordinates,
            'embeddings': embeddings
        }

    def group_complaints(self, processed_data, similarity_threshold=0.67):
        groups = []
        
        for item in tqdm(processed_data, desc="Grouping complaints"):
            added_to_group = False
            for group in groups:
                if cosine_similarity([item['embeddings']], [group[0]['embeddings']])[0][0] >= similarity_threshold:
                    group.append(item)
                    added_to_group = True
                    break
            
            if not added_to_group:
                groups.append([item])
        
        for i, group in enumerate(groups):
            for item in group:
                item['group'] = i
        
        return [item for group in groups for item in group]

    def process_data_website(self, data):
        processed_data = []
        try:
            for item in tqdm(data, desc="Processing data"):
                try:
                    full_text = f"{item['title']} {item['body']}"
                    analysis = self.process_text(full_text, self.nlp_website)
                    
                    processed_item = {
                        'title': item['title'],
                        'body': item['body'],
                        'url': item['url'],
                        'created_at': item['created'],
                        'is_complaint': analysis['is_complaint'],
                        'sentiment': analysis['sentiment'],
                        'locations': analysis['locations'],
                        'coordinates': analysis['coordinates'],
                        'embeddings': analysis['embeddings']
                    }
                    processed_data.append(processed_item)
                except Exception as e:
                    print(f"Error processing item: {e}")
                    print(f"Problematic item: {item}")
            
            return processed_data
        except Exception as e:
            print(f"An error occurred: {e}")

    def process_data_reddit(self, data):
        processed_data = []
        try:
            for item in tqdm(data, desc="Processing data"):
                try:
                    full_text = f"{item['title']} {item['body']}"
                    analysis = self.process_text(full_text, self.nlp_reddit)
                    
                    processed_item = {
                        'title': item['title'],
                        'body': item['body'],
                        'url': item['url'],
                        'created_at': item['created'],
                        'is_complaint': analysis['is_complaint'],
                        'sentiment': analysis['sentiment'],
                        'locations': analysis['locations'],
                        'coordinates': analysis['coordinates'],
                        'embeddings': analysis['embeddings']
                    }
                    processed_data.append(processed_item)
                except Exception as e:
                    print(f"Error processing item: {e}")
                    print(f"Problematic item: {item}")
            
            return processed_data
        except Exception as e:
            print(f"An error occurred: {e}")

    def save_data(self, data):
        db = self.SessionLocal()
        grouped_data = self.group_complaints(data)
        
        try:
            for item in tqdm(grouped_data, desc="Saving data"):
                try:
                    complaint = self.Complaint(
                        title=item['title'],
                        body=item['body'],
                        url=item['url'],
                        created_at=item['created_at'],
                        is_complaint=item['is_complaint'],
                        locations=item['locations'],
                        coordinates=item['coordinates'],
                        topics=item['embeddings'].tolist(),  
                        group=item['group']
                    )
                    db.add(complaint)
                except Exception as e:
                    print(f"Error saving item: {e}")
                    print(f"Problematic item: {item}")
            db.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            db.close()
        
        return grouped_data

    def get_complaints(self):
        db = self.SessionLocal()
        try:
            return db.query(self.Complaint).all()
        finally:
            db.close()