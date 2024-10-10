from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urlparse
import re
import io
from PyPDF2 import PdfReader
from tqdm import tqdm


class TorontoScraper:
    def __init__(self, url):
        self.url = url
        self.visited = set()
        self.to_visit = [url]
        self.data = []

    def get_domain(self, url):
        return urlparse(url).netloc

    def get_path(self, url):
        return urlparse(url).path

    def is_valid_url(self, url):
        path = self.get_path(url).lower()
        return (
            'city-government' in path
            and any(keyword in path for keyword in [
                'data-research-maps',
                'planning-development',
                'public-notices-bylaws',
                'research-reports'
            ])
            and not any(keyword in url for keyword in [
                'profile', 'about', 'sidebar', 'home', 'account', 'login',
                'newsletter', 'subscribe', 'register', 'weather', 'sports',
                'globalnav', 'header', 'footer', 'services-payments', 'explore-enjoy', 'open-data'
            ])
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

    def crawl_website_toronto(self, max_pages=500, delay=1):
        domain = self.get_domain(self.url)
        
        while self.to_visit and len(self.visited) < max_pages:
            url = self.to_visit.pop(0)
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

                self.data.append({
                    "url": url,
                    "title": soup.title.string if soup.title else " ",
                    "domain": domain,
                    "body": text,
                    "created": time.time()
                })

                for link in soup.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if self.get_domain(next_url) == domain and (self.is_valid_url(next_url) or not self.is_document(next_url)):
                        self.to_visit.append(next_url)
                print(f"Crawled {url}")

                for ul in soup.find_all('ul', class_='nav'):
                    for link in ul.find_all('a', href=True):
                        next_url = urljoin(url, link['href'])
                        if self.get_domain(next_url) == domain and next_url not in self.visited and next_url not in self.to_visit:
                            self.to_visit.append(next_url)
            except requests.RequestException as e:
                print(f"Failed to retrieve {url}: {e}")

            #time.sleep(delay)  

        return self.data

# urls = [
#     "https://www.toronto.ca/city-government/data-research-maps/research-reports/housing-and-homelessness-research-and-reports/shelter-system-flow-data/"
# ]

# scraper = TorontoScraper(urls[0])
# for url in urls:
#     data = scraper.crawl_website_toronto(100)
#     print(data)