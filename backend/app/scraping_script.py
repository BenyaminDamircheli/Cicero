import os
from dotenv import load_dotenv
from utils.data_scraping.reddit_scraper import RedditScraper
from utils.data_scraping.reddit_link_scraper import RedditLinkScraper
from utils.data_scraping.data_processor import Processor
from utils.data_scraping.toronto_scraper import TorontoScraper
from models.models import Base, engine
from services.data_saver import save_complaints
from tqdm import tqdm
def is_image_url(url):
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(url.lower().endswith(ext) for ext in image_extensions)


def main():
    processor = Processor()
    census_scraper1 = TorontoScraper(["data-research-maps"])
    reddit_link_scraper = RedditLinkScraper()
    # print("Initiated Toronto Scraper 1")  
    reddit_scraper = RedditScraper("toRANTo", 10)
    # print("Initiated Reddit Scraper 1")
    reddit_scraper2 = RedditScraper("askTO", 10)
    # print("Initiated Reddit Scraper 2")
    reddit_scraper3 = RedditScraper("Toronto", 50)     
    print("Initiated Reddit Scraper 3")
    try:
        # Scrape Reddit posts
        reddit_data = reddit_scraper.scrape_reddit()
        reddit_data += reddit_scraper2.scrape_reddit()
        reddit_data += reddit_scraper3.scrape_reddit()

        census_data = census_scraper1.crawl_website_toronto("https://www.toronto.ca/city-government/data-research-maps/research-reports",10)
        
        # Process regular posts and link posts separately
        regular_posts = []
        link_post_data = []
        
        for post in tqdm(reddit_data, desc="Processing Reddit posts"):
            if post['is_link_post']:
                # Check if it's a valid external link to scrape
                if ("reddit" not in post['url'] and 
                    "redd" not in post['url'] and 
                    "costar.com" not in post['url'] and 
                    "cbc.ca" not in post['url'] and 
                    not is_image_url(post['url'])):
                    try:
                        link_data = reddit_link_scraper.scrape_link(post['url'], post['url'])
                        if link_data:
                            link_post_data.append({
                                "title": link_data["title"],
                                "body": link_data["body"],
                                "url": link_data["url"],
                                "created": link_data["created"]
                            })
                    except Exception as e:
                        print(f"Failed to scrape link {post['url']}: {e}")
            else:
                regular_posts.append(post)
        
        processed_website_data1 = processor.process_data_website(census_data)

        # Process both types of posts
        processed_regular_posts = processor.process_data_reddit(regular_posts)
        processed_link_posts = processor.process_data_website(link_post_data)
        
        # Combine all processed data
        all_processed_data = processed_regular_posts + processed_link_posts + processed_website_data1
        print(all_processed_data)

        print(f"Processed {len(all_processed_data)} items.")
        
        Base.metadata.create_all(bind=engine)
        save_complaints(all_processed_data)
        
        print("Data saved successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
