import os
from dotenv import load_dotenv
from data_processor import process_data_reddit, process_data_website, get_complaints, save_data
from reddit_scraper import scrape_reddit
from toronto_scraper import crawl_website_toronto




def main():
    try:
        # Scrape data
        reddit_data = scrape_reddit("toRANTo", 10)
        reddit_data2 = scrape_reddit("askTO", 1500)
        crawl_data = crawl_website_toronto("https://www.toronto.ca/city-government/data-research-maps/", 200)

        processed_reddit_data = process_data_reddit(reddit_data)
        processed_reddit_data2 = process_data_reddit(reddit_data2)
        processed_website_data = process_data_website(crawl_data)
        all_processed_data = processed_reddit_data + processed_reddit_data2 + processed_website_data

        print(f"Processed and saved {len(all_processed_data)} items.")

        save_data(all_processed_data)
        
        complaints = get_complaints()

        print("Processed Complaints: " + str(len(complaints)))

    except ValueError as ve:
        print(f"A value error occurred: {str(ve)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
