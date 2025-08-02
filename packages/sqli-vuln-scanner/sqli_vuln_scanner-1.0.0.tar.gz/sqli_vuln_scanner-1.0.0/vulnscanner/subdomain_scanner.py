# subdomain_scanner.py
import requests
import json

def get_subdomains(domain):
    print(f"[i] Querying crt.sh for subdomains of {domain} ...")
    url = f"https://crt.sh/?q=%25.{domain}&output=json"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print("[!] crt.sh query failed.")
            return [domain]

        entries = json.loads(response.text)
        subdomains = set()

        for entry in entries:
            name = entry['name_value']
            for sub in name.split('\n'):
                if domain in sub:
                    subdomains.add(sub.strip())

        print(f"[+] Found {len(subdomains)} subdomains.")
        return list(subdomains)

    except Exception as e:
        print(f"[!] Error fetching subdomains: {e}")
        return [domain]
