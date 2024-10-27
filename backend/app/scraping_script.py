import os
from dotenv import load_dotenv
from utils.data_scraping.reddit_scraper import RedditScraper
from utils.data_scraping.data_processor import Processor
from utils.data_scraping.toronto_scraper import TorontoScraper
from models.models import Base, engine
from services.data_saver import save_complaints




def main():
    processor = Processor()
    # census_scraper1 = TorontoScraper(["data-research-maps"])
    # print("Initiated Toronto Scraper 1")  
    reddit_scraper = RedditScraper("toRANTo", 100)
    # print("Initiated Reddit Scraper 1")
    # reddit_scraper2 = RedditScraper("askTO", 1000)
    # print("Initiated Reddit Scraper 2")
    # reddit_scraper3 = RedditScraper("Toronto", 500)     
    print("Initiated Reddit Scraper 3")
    try:
        reddit_data = reddit_scraper.scrape_reddit()
        # reddit_data2 = reddit_scraper2.scrape_reddit()
        # reddit_data3 = reddit_scraper3.scrape_reddit()
        # crawl_data1 = census_scraper1.crawl_website_toronto("https://www.toronto.ca/city-government/data-research-maps/research-reports",500)

        processed_reddit_data = processor.process_data_reddit(reddit_data)
        # processed_reddit_data2 = processor.process_data_reddit(reddit_data2)
        # processed_website_data1 = processor.process_data_website(crawl_data1)
        all_processed_data = processed_reddit_data

        print(f"Processed and saved {len(all_processed_data)} items.")

        Base.metadata.create_all(bind=engine)

        save_complaints(all_processed_data)

        print("Data saved successfully.")

    except ValueError as ve:
        print(f"A value error occurred: {str(ve)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
