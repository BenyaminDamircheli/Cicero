import os
from dotenv import load_dotenv
from reddit_scraper import RedditScraper
from data_processor import Processor
from other_web_scraper import OtherWebScraper
from toronto_scraper import TorontoScraper




def main():
    processor = Processor()
    census_scraper = TorontoScraper("https://www.toronto.ca/city-government/data-research-maps/")
    # reddit_scraper = RedditScraper("toRANTo", 10)
    # reddit_scraper2 = RedditScraper("askTO", 1500)

    try:
        # Scrape data
        # reddit_data = reddit_scraper.scrape_reddit()
        # reddit_data2 = reddit_scraper2.scrape_reddit()
        crawl_data = census_scraper.crawl_website_toronto(10)

        # processed_reddit_data = processor.process_data_reddit(reddit_data)
        # processed_reddit_data2 = processor.process_data_reddit(reddit_data2)
        processed_website_data = processor.process_data_website(crawl_data)
        all_processed_data = processed_website_data

        print(f"Processed and saved {len(all_processed_data)} items.")

        processor.save_data(all_processed_data)
        
        complaints = processor.get_complaints()

        print("Processed Complaints: " + str(len(complaints)))

    except ValueError as ve:
        print(f"A value error occurred: {str(ve)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
