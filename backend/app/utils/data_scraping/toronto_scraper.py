from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urlparse
import re
import io
from PyPDF2 import PdfReader
from tqdm import tqdm
from collections import deque

class TorontoScraper: 
    """
    Scrapes the Toronto government website for data
    """
    def __init__(self, path_focus):
        self.url = None
        self.visited = set()
        self.to_visit = deque()
        self.data = []
        self.path_focus = path_focus

    def get_domain(self, url):
        return urlparse(url).netloc

    def get_path(self, url):
        return urlparse(url).path

    def is_valid_url(self, url):
        path:str = self.get_path(url).lower()
        url:str = url.lower()
        return (
            any(keyword in path for keyword in self.path_focus) and \
            not any(keyword in url for keyword in ['ward-profiles'])
        )

    def is_document(self, url):
        return any(ext in url.lower() for ext in [
            '.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls'
        ])

    # def extract_pdf_text(pdf_content):
    #     pdf_reader = PdfReader(io.BytesIO(pdf_content))
    #     text = ""
    #     for page in tqdm(pdf_reader.pages, desc="Extracting PDF text"):
    #         text += page.extract_text() + "\n"
    #     return text

    def crawl_website_toronto(self, url, max_pages=500, delay=1, max_text_length=6000):
        self.url = url
        domain = self.get_domain(url)
        self.to_visit = deque([url])   
        
        while self.to_visit and len(self.visited) < max_pages:
            url = self.to_visit.pop()
            if url in self.visited:
                continue

            try:
                response = requests.get(url)
                response.raise_for_status()
                self.visited.add(url)

                # if url.lower().endswith('.pdf'):
                #     text = extract_pdf_text(response.content)
                #     data.append({
                #         "url": url,
                #         "title": url.split('/')[-1], 
                #         "domain": domain,
                #         "body": text,
                #         "created": time.time()
                #     })
                
                soup = BeautifulSoup(response.text, 'html.parser')

                text = " ".join([p.get_text() for p in soup.find_all('p')])
                text += " ".join([li.get_text() for li in soup.find_all('li')])
                text += " ".join([h1.get_text() for h1 in soup.find_all('h1')])
                text += " ".join([div.get_text() for div in soup.find_all('div')])
                
                text = text[:max_text_length] if len(text) > max_text_length else text
                self.data.append({
                    "url": url,
                    "title": soup.title.string if soup.title else " ",
                    "domain": domain,
                    "body": text,
                    "created": time.time()
                })

                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if self.get_domain(next_url) == domain and self.is_valid_url(next_url) and not self.is_document(next_url):
                        if next_url not in self.visited and next_url not in self.to_visit:
                            self.to_visit.append(next_url)
                print(f"Crawled {url}")

                for div in soup.find_all('div'):
                    for link in div.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        if self.get_domain(next_url) == domain and next_url not in self.visited and next_url not in self.to_visit and self.is_valid_url(next_url):
                            self.to_visit.append(next_url)

                for ul in soup.find_all('ul'):
                    for link in ul.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        if self.get_domain(next_url) == domain and next_url not in self.visited and next_url not in self.to_visit and self.is_valid_url(next_url):
                            self.to_visit.append(next_url)
                            
                for ol in soup.find_all('ol'):
                    for link in ol.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        if self.get_domain(next_url) == domain and next_url not in self.visited and next_url not in self.to_visit and self.is_valid_url(next_url):
                            self.to_visit.append(next_url)
            except requests.RequestException as e:
                print(f"Failed to retrieve {url}: {e}")

            #time.sleep(delay)  

        return self.data

# urls = [
#     "https://www.toronto.ca/city-government/data-research-maps/research-reports",
 
# ]

# scraper = TorontoScraper(["data-research-maps"])
# processor = Processor()
# for url in urls:
#     data = scraper.crawl_website_toronto(url, max_pages=500)
#     processed_data = processor.process_data_website(data)
#     for i in processed_data:
#         print(i['locations'])
#         print(i['coordinates'])
#         print(i['body'])
#         print('---')