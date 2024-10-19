from openai import OpenAI
from pydantic import BaseModel
import json
from utils.types import GroupedComplaint, Summary, Urgency
from utils.data_saver import ComplaintSummary, save_complaint_summary, summary_exists, get_complaint_summary, SessionLocal

session = SessionLocal()

API_KEY = "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"
client = OpenAI(api_key=API_KEY)

def generate_complaint_summary(complaint: GroupedComplaint):
    sources = complaint.sources
    result = ""
    for source in sources:
        result += f"Title: {source.title}\nBody: {source.body[:1000]}\n\n ----------------------\n\n"

    prompt = f"""
    Analyze the following complaints:
    {result}

    1. Provide a short title that best describes the complaints.
    2. Provide a short summary of the complaints (100 words max).
    3. Assign an urgency score from 1-5 and explain why (50 words max).
    4. Propose a potential solution(s) to address the complaints, keep this in paragraph form, no lists (100 words max).
    """
    # don't make api calls if the summary already exists
    if summary_exists(complaint.group):
        return get_complaint_summary(complaint.group)
    
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
