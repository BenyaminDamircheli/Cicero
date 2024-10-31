import praw
from tqdm import tqdm
from utils.data_scraping.toronto_scraper import TorontoScraper
import re
import urllib.parse

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
            body = post.selftext
            url = post.url
            
            is_link_post = not post.is_self and not any(url.lower().endswith(ext) for ext in ['.jpeg', '.jpg', '.png', '.gif'])
            
            data.append({
                "title": post.title,
                "score": post.score,
                "body": body,
                "created": post.created_utc,
                "id": post.id,
                "url": url,
                "is_link_post": is_link_post
            })

        return data





