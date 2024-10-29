from utils.data_scraping.reddit_link_scraper import RedditLinkScraper
from utils.data_scraping.reddit_scraper import RedditScraper

def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def run_reddit_link_test():
    reddit_scraper = RedditScraper("toronto", 100)
    reddit_link_scraper = RedditLinkScraper()

    reddit_data = reddit_scraper.scrape_reddit()

    
    #NOTE for some reason costar.com and cbc.ca are not working for the scraper.
    for item in reddit_data:
        if "reddit" not in item['url'] and "redd" not in item['url'] and "costar.com" not in item['url'] and "cbc.ca" not in item['url'] and not is_image_url(item['url']):
            data = reddit_link_scraper.scrape_link(item['url'])
            print(data)
