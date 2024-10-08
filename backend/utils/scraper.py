from bs4 import BeautifulSoup
import requests
import time
from urllib.parse import urljoin, urlparse
import re


# just for displaying the data properly
def get_domain(url):
    return urlparse(url).netloc

def get_path(url):
    return urlparse(url).path

def is_valid_url(url):
    path = get_path(url).lower()
    return not any(keyword in path for keyword in ['/profile', '/about', '/home', "/account", "/login", "/newsletter", "/subscribe", "/register", "/weather", '/sports'])
    
def crawl_website(url, max_pages=500, delay=1):
    domain = get_domain(url)
    base_path = get_path(url)
    visited = set()
    to_visit = [url]
    data = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue

        try:
            response = requests.get(url)
            response.raise_for_status()
            visited.add(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            text = " ".join([p.get_text() for p in soup.find_all('p')])

            data.append({
                "url": url,
                "title": soup.title.string if soup.title else "",
                "domain": domain,
                "body": text,
                "created": time.time()
            })

            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if get_domain(next_url) == domain and is_valid_url(next_url):
                    to_visit.append(next_url)
            print(f"Crawled {url}")
            

            for ul in soup.find_all('ul', class_='nav'):
                for link in ul.find_all('a', href=True):
                    next_url = urljoin(url, link['href'])
                    if get_domain(next_url) == domain and next_url not in visited and next_url not in to_visit:
                        to_visit.append(next_url)
        except requests.RequestException as e:
            print(f"Failed to retrieve {url}: {e}")

    return data

# urls = [
#     "https://www.toronto.ca/city-government/data-research-maps/"
# ]

# for url in urls:
#     data = crawl_website(url)
#     print(data)


