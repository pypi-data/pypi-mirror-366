# vulnscanner/xss_scanner.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from colorama import Fore, Style

def scan_xss(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")
        forms = soup.find_all("form")
        payload = "<script>alert(1)</script>"

        for form in forms:
            action = form.get("action")
            method = form.get("method", "get").lower()
            inputs = form.find_all("input")
            data = {}

            for input_tag in inputs:
                name = input_tag.get("name")
                if name:
                    data[name] = payload

            target = urljoin(url, action)
            if method == "post":
                r = requests.post(target, data=data)
            else:
                r = requests.get(target, params=data)

            if payload in r.text:
                print(f"{Fore.LIGHTRED_EX}[!!] XSS Vulnerability found in form at {target}{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[-] No XSS found in form at {target}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.YELLOW}[!] XSS scan error on {url}: {e}{Style.RESET_ALL}")
