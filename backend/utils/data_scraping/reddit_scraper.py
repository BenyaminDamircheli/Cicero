import praw
from tqdm import tqdm


class RedditScraper:
    def __init__(self, subreddit, limit = 2300):
        self.subreddit = subreddit
        self.limit = limit

    def scrape_reddit(self):
        reddit = praw.Reddit(
        client_id = "9YcMFjtzVTx8rrSwogcrQA",
        client_secret = "Zq-HkQnwdBsO_ZB6nCPtZm2wjA-e_A",
        user_agent = "city_complaints_scraper"
    )


        subreddit = reddit.subreddit(self.subreddit)
        posts = subreddit.new(limit = self.limit)

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


