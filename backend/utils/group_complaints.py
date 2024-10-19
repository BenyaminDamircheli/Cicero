from utils.types import GroupedComplaint, Source
from itertools import groupby

def group_complaints(complaints):
    def group_key(complaint):
        return complaint.group

    def merge_complaints(group):
        with_coords = [c for c in group if c.coordinates]
        no_coords = [c for c in group if not c.coordinates]

        result = []
        for complaint in with_coords:
            nearby = [c for c in with_coords if c != complaint]

            all_sources = [Source(title=c.title, body=c.body, url=c.url) for c in nearby + no_coords + [complaint]]
            sources = all_sources[:5]

            result.append(
                GroupedComplaint(
                    id = f'{complaint.group}_{complaint.id}',
                    coordinates= complaint.coordinates[0], 
                    sources = sources
                )
            )

        return result
        
    sorted_complaints = sorted(complaints, key=group_key)
    grouped = groupby(sorted_complaints, key=group_key)

    return [
        complaint 
        for _,group in grouped
        for complaint in merge_complaints(list(group))
    ]