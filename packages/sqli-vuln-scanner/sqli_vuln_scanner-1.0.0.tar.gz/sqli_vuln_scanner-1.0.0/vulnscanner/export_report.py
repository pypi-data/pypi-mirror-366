# vulnscanner/export_report.py
import csv
from fpdf import FPDF
import os
from datetime import datetime

def export_to_csv(findings, filename="scan_report.csv"):
    keys = ["url", "param", "type", "payload"]
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        for f in findings:
            writer.writerow({k: f.get(k, "") for k in keys})
    print(f"[+] Report saved to {filename}")

def export_to_pdf(findings, filename="scan_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Vulnerability Scan Report", ln=1, align='C')
    pdf.ln(10)

    for finding in findings:
        pdf.set_font("Arial", style='B', size=11)
        pdf.cell(200, 8, txt=f"Type: {finding['type']}", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=f"URL: {finding['url']}", ln=1)
        pdf.cell(200, 8, txt=f"Param: {finding['param']}", ln=1)
        pdf.cell(200, 8, txt=f"Payload: {finding['payload']}", ln=1)
        pdf.ln(5)

    pdf.output(filename)
    print(f"[+] Report saved to {filename}")
