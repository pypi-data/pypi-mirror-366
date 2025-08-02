# 🔍 FullVulnScanner

A modular Python-based web vulnerability scanner that performs:

✅ Subdomain enumeration  
✅ Website crawling  
✅ SQL Injection detection (error-based)  

---

📌 Features

- 🔎 Subdomain Enumeration using `crt.sh`
- 🌐 Intelligent Site Crawler (with depth control)
- 💉 SQL Injection Detection:
  - Error-Based
  - Blind Time-Based (`SLEEP`)
- 🛡️ WAF/Firewall Detection via Connection Resets
- 📄 JSON Reporting (`scan_report.json`)
- ✅ Graceful handling of network errors and dead links

---
### ⚙️ Setup

```bash
git clone https://github.com/rupesh109/SQLi-Vulnerability-Scanner.git
cd SQLi-Vulnerability-Scanner
pip install -r requirements.txt
▶️ Run the Scanner
python main.py
💡 You’ll be prompted to enter a domain like:
univjoy.com

### 📁 Project Structure
├── main.py                  # Main entry point
├── crawler.py               # Crawls target site for URLs
├── sqli_scanner.py          # Runs SQLi payloads on parameterized URLs
├── subdomain_scanner.py     # Uses crt.sh to find subdomains
├── requirements.txt         # Required Python packages
├── output/
│   └── scan_report.json     # Auto-generated report
├── payloads/                # SQLi payload list
└── README.md                # You're here!
## 🖥️ Screenshot
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/04552824-821c-4679-a8fc-f0d8de0504a0" />

####🧠 Technologies Used
Python requests, urllib, bs4

Terminal coloring with colorama

HTML parsing with BeautifulSoup

JSON-based output for reports

###🛡️ Legal Disclaimer
This tool is for educational purposes only. Unauthorized scanning or exploiting websites without permission is illegal. The author is not responsible for misuse.

###📜 License
MIT License © Rupesh Kumar Jha



