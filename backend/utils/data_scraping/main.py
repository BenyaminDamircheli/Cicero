import os
from dotenv import load_dotenv
from reddit_scraper import RedditScraper
from data_processor import Processor
from other_web_scraper import OtherWebScraper
from toronto_scraper import TorontoScraper




def main():
    processor = Processor()
    census_scraper1 = TorontoScraper(["data-research-maps"])
    print("Initiated Toronto Scraper 1")  
    reddit_scraper = RedditScraper("toRANTo", 1000)
    print("Initiated Reddit Scraper 1")
    reddit_scraper2 = RedditScraper("askTO", 1000)
    print("Initiated Reddit Scraper 2")
    try:
        reddit_data = reddit_scraper.scrape_reddit()
        reddit_data2 = reddit_scraper2.scrape_reddit()
        crawl_data1 = census_scraper1.crawl_website_toronto("https://www.toronto.ca/city-government/data-research-maps/research-reports",500)

        processed_reddit_data = processor.process_data_reddit(reddit_data)
        processed_reddit_data2 = processor.process_data_reddit(reddit_data2)
        processed_website_data1 = processor.process_data_website(crawl_data1)
        all_processed_data = processed_reddit_data + processed_reddit_data2 + processed_website_data1

        print(f"Processed and saved {len(all_processed_data)} items.")

        processor.save_data(all_processed_data)
        
        print("Data saved successfully.")

    except ValueError as ve:
        print(f"A value error occurred: {str(ve)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
