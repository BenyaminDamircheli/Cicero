import nltk
import numpy as np
import spacy
from dotenv import load_dotenv
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from sentence_transformers import SentenceTransformer
from sumy.summarizers.lsa import LsaSummarizer
from geopy.geocoders import Nominatim
from tqdm import tqdm
import re
from .toronto_scraper import TorontoScraper

class Processor:
    def __init__(self):
        load_dotenv()

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

    def process_text(self, text, nlp):
        if not isinstance(text, str):
            text = str(text)  

        doc = nlp(text)
        
        sentiment = self.sia.polarity_scores(text)
        is_complaint = sentiment['compound'] < 0.00  # play with this a bit
        
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
        import re

        # def extract_urls(text):
        #     url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        #     return url_pattern.findall(text)
        
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