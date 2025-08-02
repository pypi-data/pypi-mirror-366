# main.py
import argparse
import json
from vulnscanner.crawler import crawl_site
from vulnscanner.sqli_scanner import scan_url
from vulnscanner.xss_scanner import scan_xss
from vulnscanner.subdomain_scanner import get_subdomains
from vulnscanner.form_scanner import scan_forms
from vulnscanner.report_generator import generate_html_report
from vulnscanner.export_report import export_to_csv, export_to_pdf
from concurrent.futures import ThreadPoolExecutor

scan_results = {
    "sqli": [],
    "form": [],
    "xss": []
}

def main():
    parser = argparse.ArgumentParser(description="FullVulnScanner - SQLi, XSS, and Form Scanner")
    parser.add_argument("domain", help="Target domain (e.g., univjoy.com)")
    parser.add_argument("--scan-sqli", action="store_true", help="Enable SQLi scanning")
    parser.add_argument("--scan-xss", action="store_true", help="Enable XSS scanning")
    parser.add_argument("--scan-forms", action="store_true", help="Enable Form scanning")
    args = parser.parse_args()

    domain = args.domain
    print("[+] Finding subdomains...")
    subdomains = get_subdomains(domain)

    for sub in subdomains:
        base_url = f"http://{sub}"
        print(f"\n[+] Crawling {base_url} ...")
        urls = crawl_site(base_url, max_urls=30, max_depth=2)

        def scan_target(url):
            if args.scan_sqli and "?" in url:
                print(f"\n[+] Scanning {url} for SQL Injection...")
                sqli_results = scan_url(url)
                scan_results["sqli"].extend(sqli_results)

            if args.scan_xss and "?" in url:
                print(f"\n[+] Scanning {url} for XSS...")
                xss_results = scan_xss(url)
                scan_results["xss"].extend(xss_results)

            if args.scan_forms:
                print(f"\n[+] Checking {url} for login/search forms...")
                form_vulns = scan_forms(url)
                if form_vulns:
                    print(f"[!!] Form-based vulnerability found on {url}")
                    scan_results["form"].extend(form_vulns)

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(scan_target, urls)

    # Save reports
    with open("scan_report.json", "w") as f:
        json.dump(scan_results, f, indent=4)

    generate_html_report()
    export_to_csv()
    export_to_pdf()

if __name__ == "__main__":
    main()
