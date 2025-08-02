import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Button, Checkbutton, Label, Entry, Progressbar
from tkinter.scrolledtext import ScrolledText
import webbrowser
import threading
import sys
import os

from vulnscanner.main import scan_results, main as cli_main
from vulnscanner.export_report import export_to_pdf, export_to_csv
from vulnscanner.report_generator import generate_html_report

# GUI redirector for logging
class TextRedirector:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.config(state='normal')
        self.widget.insert('end', text)
        self.widget.yview('end')
        self.widget.config(state='disabled')

    def flush(self):
        pass

# GUI setup
window = tk.Tk()
window.title("Full Vuln Scanner GUI")
window.geometry("780x620")

Label(window, text="Enter Target Domain (e.g. example.com):").pack(pady=5)
domain_entry = Entry(window, width=50)
domain_entry.pack(pady=5)

# Scan Options
scan_sqli_var = tk.BooleanVar()
scan_xss_var = tk.BooleanVar()
scan_forms_var = tk.BooleanVar()

Checkbutton(window, text="Scan for SQLi", variable=scan_sqli_var).pack()
Checkbutton(window, text="Scan for XSS", variable=scan_xss_var).pack()
Checkbutton(window, text="Scan for Forms", variable=scan_forms_var).pack()

# Output Log
Label(window, text="Scanner Output Log:").pack(pady=5)
log_output = ScrolledText(window, height=18, width=90, state='disabled', wrap='word')
log_output.pack(pady=5)

# Progress Bar (hidden initially)
progress_bar = Progressbar(window, mode='indeterminate', length=250)

sys.stdout = TextRedirector(log_output)
sys.stderr = TextRedirector(log_output)

# Scan logic
def run_scan():
    domain = domain_entry.get().strip()
    if not domain:
        messagebox.showwarning("Input Error", "Please enter a domain.")
        return

    args = ["vulnscan", domain]
    if scan_sqli_var.get():
        args.append("--scan-sqli")
    if scan_xss_var.get():
        args.append("--scan-xss")
    if scan_forms_var.get():
        args.append("--scan-forms")

    progress_bar.pack(pady=5)
    progress_bar.start()

    def scan_thread():
        try:
            sys.argv = args
            cli_main()
            messagebox.showinfo("Scan Complete", "Scanning finished successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Scan failed: {str(e)}")
        finally:
            progress_bar.stop()
            progress_bar.pack_forget()

    threading.Thread(target=scan_thread).start()

# Export buttons
def export_pdf_gui():
    try:
        export_to_pdf()
        messagebox.showinfo("Export", "PDF exported successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def export_csv_gui():
    try:
        export_to_csv()
        messagebox.showinfo("Export", "CSV exported successfully.")
    except Exception as e:
        messagebox.showerror("Export Failed", str(e))

def open_report():
    report_path = os.path.abspath("report.html")
    if os.path.exists(report_path):
        webbrowser.open_new_tab(f"file://{report_path}")
    else:
        messagebox.showwarning("Not Found", "Report not generated yet.")

# Buttons
Button(window, text="Run Scan", command=run_scan).pack(pady=10)
Button(window, text="Open HTML Report", command=open_report).pack(pady=2)
Button(window, text="Export PDF", command=export_pdf_gui).pack(pady=2)
Button(window, text="Export CSV", command=export_csv_gui).pack(pady=2)

window.mainloop()
