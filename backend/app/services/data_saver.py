from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from models.models import SessionLocal, Complaint, ComplaintSummary, engine, Base
from schemas.complaint_types import GroupedComplaint

def save_complaints(data):
    db = SessionLocal()
    grouped_data = group_complaints(data)
    
    # filter out non-complaint data
    print(f"Total items before filtering: {len(grouped_data)}")
    filtered_complaints = [
        item for item in grouped_data
        if (item['is_complaint'] or "toRANTo" in item['url'] or "toronto.ca" in item['url']) and (not any(ext in item['url'] for ext in ["jpg", "jpeg", "png", "gif"]) or "reddit.com" not in item['url'])
    ]
    print(f"Items after filtering: {len(filtered_complaints)}")


    groups = set([item['group'] for item in filtered_complaints])

    summaries = [
        ComplaintSummary(
            id=group,
        )
        for group in groups
    ]

    db.bulk_save_objects(summaries)
    db.commit()
    
    try:
        complaints = [
            Complaint(
                title=item['title'],
                body=item['body'],
                url=item['url'],
                created_at=item['created_at'],
                is_complaint=item['is_complaint'],
                locations=item['locations'],
                coordinates=item['coordinates'],
                topics=item['embeddings'].tolist(),  
                group=item['group'],
                summary=None
            )
            for item in filtered_complaints
        ]
        db.bulk_save_objects(complaints)
        db.commit()
        print(f"Successfully saved {len(complaints)} complaints.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred during bulk saving: {e}")
    finally:
        db.close()
        
    return grouped_data


def group_complaints(processed_data, similarity_threshold=0.69):
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

def save_complaint_summary(complaint: GroupedComplaint, summary_data: dict):
    db = SessionLocal()
    try:
        complaint_summary = db.query(ComplaintSummary).filter(ComplaintSummary.id == complaint.group).first()
        if not complaint_summary:
            complaint_summary = ComplaintSummary(id=complaint.group)
            db.add(complaint_summary)
        
        complaint_summary.title = summary_data['title']
        complaint_summary.summary = summary_data['summary']
        complaint_summary.urgency_description = summary_data['urgency']['explanation']
        complaint_summary.urgency_score = summary_data['urgency']['score']
        complaint_summary.solution = summary_data['solutions']
        
        db.commit()
        return complaint_summary
    except Exception as e:
        db.rollback()
        print(f"Error saving complaint summary: {e}")
    finally:
        db.close()

def summary_exists(group):
    db = SessionLocal()
    try:
        summary = db.query(ComplaintSummary).filter(ComplaintSummary.id == group).first()
        return summary is not None and summary.title is not None
    finally:
        db.close()

def get_complaint_summary(group):
    db = SessionLocal()
    try:
        summary = db.query(ComplaintSummary).filter(ComplaintSummary.id == group).first()
        if summary:
            print("Summary found")
            return {
                "title": summary.title,
                "summary": summary.summary,
                "urgency": {
                    "score": summary.urgency_score,
                    "explanation": summary.urgency_description
                },
                "solutions": summary.solution
            }
        else:
            print("No summary found")
            return None
    finally:
        db.close()

def get_complaints_by_group(group):
    db = SessionLocal()
    query = db.query(Complaint).filter(Complaint.group == group).all()
    return query

def get_complaints():
    db = SessionLocal()
    query = db.query(Complaint).all()
    return query

