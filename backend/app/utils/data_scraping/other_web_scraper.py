# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from urllib.parse import urljoin, urlparse
# import time
# from tqdm import tqdm

# class OtherWebScraper:
#     def __init__(self, url):
#         self.url = url
#         self.visited = set()
#         self.to_visit = [url]
#         self.data = []

#     def get_domain(self, url):
#         return urlparse(url).netloc

#     def get_path(self, url):
#         return urlparse(url).path

#     def is_document(self, url):
#         return any(ext in url.lower() for ext in [
#             '.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls'
#         ])

#     def crawl_website_other(self, max_pages=500, delay=1):
#         chrome_options = Options()
#         chrome_options.add_argument("--headless")
#         driver = webdriver.Chrome(options=chrome_options)
        
#         domain = self.get_domain(self.url)

#         try:
#             while self.to_visit and len(self.visited) < max_pages:
#                 url = self.to_visit.pop(0)
#                 if url in self.visited:
#                     continue

#                 try:
#                     driver.get(url)
#                     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#                     self.visited.add(url)

#                     soup = BeautifulSoup(driver.page_source, 'html.parser')

#                     # Find the main content area (adjust the selector as needed)
#                     main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('article')

#                     if main_content:
#                         text = " ".join([p.text for p in main_content.find_all('p', 'h1', 'h2', 'h3', 'div', 'span', 'li', 'a')])

#                         self.data.append({
#                             "url": url,
#                             "title": driver.title if driver.title else " ",
#                             "domain": domain,
#                             "body": text,
#                             "created": time.time()
#                         })

#                         # Only look for links within the main content area
#                         for link in main_content.find_all('a', href=True):
#                             next_url = urljoin(url, link['href'])
#                             if self.get_domain(next_url) == domain and not self.is_document(next_url):
#                                 self.to_visit.append(next_url)
#                         print(f"Crawled {url}")

#                     time.sleep(delay)
#                 except Exception as e:
#                     print(f"Failed to retrieve {url}: {e}")

#         finally:
#             driver.quit()

#         return self.data

# urls = [
#     "https://www.toronto.ca/city-government/data-research-maps/research-reports/housing-and-homelessness-research-and-reports/"
# ]
# scraper = OtherWebScraper(urls[0])
# data = scraper.crawl_website_other(max_pages=1000)
# for i in data:
#     print(i['url'])
#     print(i['title'])
#     print(i['body'])
#     print('---')