
import json
from datetime import datetime

def generate_html_report(json_path="scan_report.json", output_path="scan_report.html"):
    with open(json_path, "r") as f:
        data = json.load(f)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sqli_count = len(data["sqli"])
    form_count = len(data["form"])

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Scan Report</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
                background-color: #f7f9fc;
                color: #2c3e50;
                transition: background 0.3s, color 0.3s;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            .dark {{
                background-color: #121212;
                color: #e0e0e0;
            }}
            .section {{
                background: #ffffff;
                padding: 20px;
                margin-bottom: 30px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.05);
            }}
            .dark .section {{
                background: #1e1e1e;
            }}
            .vuln {{
                border-left: 5px solid #e74c3c;
                padding-left: 15px;
                margin: 15px 0;
                background: #fff5f5;
            }}
            .dark .vuln {{
                background: #2b2b2b;
            }}
            .label {{
                font-weight: bold;
                color: #34495e;
            }}
            .dark .label {{
                color: #90caf9;
            }}
            #toggle {{
                float: right;
                padding: 10px 15px;
                margin: 10px;
                border: none;
                background: #3498db;
                color: white;
                cursor: pointer;
                border-radius: 5px;
            }}
        </style>
    </head>
    <body>
        <button id="toggle" onclick="toggleMode()">🌙 Toggle Dark Mode</button>
        <h1>🛡️ SQLi Vulnerability Scanner Report</h1>
        <p><strong>Scan Time:</strong> {timestamp}</p>

        <div class="section">
            <h2>📊 Summary</h2>
            <canvas id="chart" width="400" height="200"></canvas>
            <script>
                const ctx = document.getElementById('chart').getContext('2d');
                new Chart(ctx, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['SQLi', 'Form Vulnerabilities'],
                        datasets: [{{
                            label: 'Findings',
                            data: [{sqli_count}, {form_count}],
                            backgroundColor: ['#e74c3c', '#3498db'],
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{ position: 'bottom' }}
                        }}
                    }}
                }});
            </script>
        </div>

        <div class="section">
            <h2>💉 SQL Injection Results</h2>
            {"<p>No SQLi vulnerabilities found.</p>" if not data["sqli"] else ""}
    """

    for vuln in data["sqli"]:
        html += f"""
            <div class="vuln">
                <p><span class="label">URL:</span> {vuln['url']}</p>
                <p><span class="label">Parameter:</span> {vuln['param']}</p>
                <p><span class="label">Type:</span> {vuln['type']}</p>
                <p><span class="label">Payload:</span> <code>{vuln['payload']}</code></p>
            </div>
        """

    html += """
        </div>
        <div class="section">
            <h2>🔐 Form-Based Vulnerabilities</h2>
    """

    if not data["form"]:
        html += "<p>No vulnerable forms found.</p>"
    else:
        for form in data["form"]:
            html += f"""
            <div class="vuln">
                <p><span class="label">URL:</span> {form['url']}</p>
                <p><span class="label">Method:</span> {form['method'].upper()}</p>
                <p><span class="label">Used Username:</span> {form['user']}</p>
                <p><span class="label">Used Password:</span> {form['pass']}</p>
            </div>
            """

    html += """
        </div>
        <script>
            function toggleMode() {
                document.body.classList.toggle('dark');
            }
        </script>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ HTML report with dark mode and charts saved to: {output_path}")
