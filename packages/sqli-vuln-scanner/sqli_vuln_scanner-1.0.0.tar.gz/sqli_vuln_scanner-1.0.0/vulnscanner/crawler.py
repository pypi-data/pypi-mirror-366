# vulnscanner/crawler.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def crawl_site(start_url, max_urls=50, max_depth=2):
    visited = set()
    to_visit = [(start_url, 0)]
    discovered_urls = []

    print(f"{Fore.CYAN}[i] Starting crawl at {start_url}{Style.RESET_ALL}")

    while to_visit and len(visited) < max_urls:
        current_url, depth = to_visit.pop(0)

        if current_url in visited or depth > max_depth:
            continue

        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')

            for link_tag in soup.find_all("a"):
                href = link_tag.get("href")

                if href and not href.startswith("mailto:") and not href.startswith("javascript:"):
                    new_url = urljoin(current_url, href)
                    new_url = new_url.split('#')[0]  # Remove fragment

                    if is_valid_url(new_url) and new_url not in visited:
                        to_visit.append((new_url, depth + 1))
                        discovered_urls.append(new_url)

        except Exception as e:
            print(f"{Fore.YELLOW}[!] Failed to crawl {current_url}: {e}{Style.RESET_ALL}")

    # Return only URLs that have parameters
    param_urls = [url for url in discovered_urls if "?" in url]
    print(f"{Fore.GREEN}[+] Discovered {len(param_urls)} parameterized URLs.{Style.RESET_ALL}")
    return param_urls
