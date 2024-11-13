import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, ARRAY, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from urllib.parse import quote_plus
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_user = os.environ.get("user")
db_password = os.environ.get("password")
db_host = os.environ.get("host")
db_port = os.environ.get("port")
db_name = os.environ.get("dbname", "postgres")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# This is the individual complaints
class Complaint(Base):
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
    group = Column(Integer, ForeignKey("complaint_summaries.id"))

    summary = relationship("ComplaintSummary", back_populates="complaints")

# this is the summary of multiple complaints in a specific location about a specific issue
class ComplaintSummary(Base):
    __tablename__ = "complaint_summaries"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    summary = Column(String)
    urgency_score = Column(Integer)
    solution = Column(String)
    location = Column(ARRAY(String))

    complaints = relationship("Complaint", back_populates="summary")