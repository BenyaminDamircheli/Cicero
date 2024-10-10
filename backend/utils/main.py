import os
from dotenv import load_dotenv
from data_processor import process_and_save_data, get_complaints, process_text
from reddit_scraper import scrape_reddit
from scraper import crawl_website




def main():
    try:
        # Scrape data
        reddit_data = scrape_reddit("toRANTo", 2000)
        reddit_data2 = scrape_reddit("askTO", 2000)
        crawl_data = crawl_website("https://www.toronto.ca/city-government/", 500)
        
        all_data = reddit_data + reddit_data2 + crawl_data
        # Process and save data
        processed_data = process_and_save_data(all_data)

        print(f"Processed and saved {len(all_data)} items.")

        # Retrieve complaints
        complaints = get_complaints()

        print("Processed Complaints: " + str(len(complaints)))

    except ValueError as ve:
        print(f"A value error occurred: {str(ve)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
