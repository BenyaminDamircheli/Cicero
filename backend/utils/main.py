import os
from dotenv import load_dotenv
from data_processor import process_and_save_data, get_complaints, process_text
from reddit_scraper import scrape_reddit
from scraper import crawl_website



def main():
    try:
        # Scrape data
        reddit_data = scrape_reddit("toRANTo", 100)
        scraped_data = crawl_website("https://www.toronto.ca/city-government/data-research-maps/", 100)
        
        all_data = reddit_data + scraped_data
        # Process and save data
        processed_data = process_and_save_data(all_data)

        

        print(f"Processed and saved {len(all_data)} items.")

        # Retrieve complaints
        complaints = get_complaints()

        print("Processed Complaints:")
        

        if len(complaints) > 10:
            print(f"... and {len(complaints) - 10} more")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
