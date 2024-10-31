from openai import OpenAI
from pydantic import BaseModel
import json
import os
import dotenv
from schemas.complaint_types import GroupedComplaint, Summary
from services.data_saver import ComplaintSummary, save_complaint_summary, summary_exists, get_complaint_summary, SessionLocal

dotenv.load_dotenv()
session = SessionLocal()

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

def generate_complaint_summary(complaint: GroupedComplaint):
    sources = complaint.sources
    result = ""
    for source in sources:
        result += f"Title: {source.title}\nBody: {source.body[:1000]}\n\n ----------------------\n\n"

    prompt = f"""
    Analyze the following complaints:
    {result}

    1. Provide a short title that best describes the complaints, emphasize the complaints keep it as short as possible.
    2. Provide a short summary of the complaints (90 words max).
    3. Assign an urgency score from 1-5 (5 is most urgent).
    4. Propose a potential solution(s) to address the complaints, keep this short in paragraph form, no lists (55 words max).
    """
    print("Checking if summary already exists")
    # don't make api calls if the summary already exists
    if summary_exists(complaint.group):
        return get_complaint_summary(complaint.group)
    
    print("Generating summary")
    
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
