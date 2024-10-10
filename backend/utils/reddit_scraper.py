import praw
from tqdm import tqdm

def scrape_reddit(subreddit, limit = 2300):
    reddit = praw.Reddit(
        client_id = "9YcMFjtzVTx8rrSwogcrQA",
        client_secret = "Zq-HkQnwdBsO_ZB6nCPtZm2wjA-e_A",
        user_agent = "webscraper"
    )

    subreddit = reddit.subreddit(subreddit)
    posts = subreddit.new(limit = limit)

    data = []

    for post in tqdm(posts, desc="Scraping Reddit"):
        data.append({
            "title": post.title,
            "score": post.score,
            "body": post.selftext,
            "created": post.created_utc,
            "id": post.id,
            "url": post.url,
        })

    return data

# Remove the summarize_text function
