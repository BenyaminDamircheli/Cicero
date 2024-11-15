from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import time

class RedditLinkScraper:
    def __init__(self):
        pass  

    def get_domain(self, url):
        return urlparse(url).netloc

    def scrape_link(self, url, reddit_url):
        """
        Scrapes content from a single URL and returns the data
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            domain = self.get_domain(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            text = " ".join([p.get_text() for p in soup.find_all('p')])
            
            max_text_length = 6000
            text = text[:max_text_length] if len(text) > max_text_length else text

            print(f"Scraped link {url}")
            
            return {
                "url": url,
                "reddit_url": reddit_url,
                "title": soup.title.string if soup.title else " ",
                "domain": domain,
                "body": text,
                "created": time.time()
            }

        except requests.RequestException as e:
            print(f"Failed to retrieve {url}: {e}")
            return None
