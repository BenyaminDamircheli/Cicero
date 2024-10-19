from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from models import SessionLocal, Complaint, ComplaintSummary

def save_complaints(data):
    db = SessionLocal()
    grouped_data = group_complaints(data)
    
    try:
        for item in tqdm(grouped_data, desc="Saving data"):
            try:
                complaint = Complaint(
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


def save_complaint_summary(data):
    db = SessionLocal()

    # don't redundantly save summaries. not sure if this is necessary however.
    if summary_exists(data['group']):
        return
    
    try:
        complaint_summary = ComplaintSummary(
            group=data['group'],
            title=data['title'],
            summary=data['summary'],
            urgency_description=data['urgency_description'],
            urgency_score=data['urgency_score'],
            solution=data['solution']
        )
        db.add(complaint_summary)
        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()


def summary_exists(group):
    db = SessionLocal()
    query = db.query(ComplaintSummary).filter(ComplaintSummary.group == group).first()
    return query is not None

def get_complaint_summary(group):
    db = SessionLocal()
    query = db.query(ComplaintSummary).filter(ComplaintSummary.group == group).first()
    return query


def get_complaints_by_group(group):
    db = SessionLocal()
    query = db.query(Complaint).filter(Complaint.group == group).all()
    return query

def get_complaints():
    db = SessionLocal()
    query = db.query(Complaint).all()
    return query