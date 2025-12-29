"""Update index.html with dynamically generated list of wrapped reports"""
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def scan_wrapped_reports(reports_dir: str = "wrapped_reports") -> Dict[str, List[Dict[str, str]]]:
    """Scan wrapped_reports directory and organize by year"""
    reports_by_year = defaultdict(list)
    
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return {}
    
    # Scan for year subdirectories
    for year_dir in sorted(reports_path.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        
        year = year_dir.name
        
        # Find all HTML files in this year
        html_files = sorted(year_dir.glob("*.html"))
        
        for html_file in html_files:
            filename = html_file.name
            name = filename.replace(".html", "").replace(f"_{year}", "")
            
            # Determine if this is the server summary
            is_server_summary = "server_summary" in filename.lower()
            
            reports_by_year[year].append({
                "name": name,
                "filename": filename,
                "path": f"{year}/{filename}",
                "is_server_summary": is_server_summary
            })
    
    # Sort each year's reports: server summary first, then alphabetically
    for year in reports_by_year:
        reports_by_year[year].sort(key=lambda x: (not x["is_server_summary"], x["name"].lower()))
    
    return dict(reports_by_year)


def generate_index_html(reports_by_year: Dict[str, List[Dict[str, str]]]) -> str:
    """Generate the complete index.html content"""
    
    # Build year sections HTML
    year_sections_html = ""
    
    for year, reports in reports_by_year.items():
        # Count reports
        report_count = len(reports)
        
        # Build report cards HTML
        cards_html = ""
        
        for report in reports:
            if report["is_server_summary"]:
                # Featured server summary card
                cards_html += f'''
                    <!-- Featured: Server Summary -->
                    <a href="wrapped_reports/{report["path"]}" class="report-card featured">
                        <span class="icon">🌟</span>
                        <h3>Server Summary</h3>
                        <p>Complete overview of all server activity</p>
                    </a>
'''
            else:
                # Regular user report card
                cards_html += f'''
                    <a href="wrapped_reports/{report["path"]}" class="report-card">
                        <span class="icon">👤</span>
                        <h3>{report["name"]}</h3>
                        <p>Personal wrapped report</p>
                    </a>
'''
        
        # Build year section
        year_sections_html += f'''
            <!-- {year} Reports -->
            <div class="year-section">
                <div class="year-header">
                    <h2>{year}</h2>
                    <span class="count">{report_count} Report{"s" if report_count != 1 else ""}</span>
                </div>
                
                <div class="reports-grid">{cards_html}
                </div>
            </div>
'''
    
    # Generate complete HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>Plex Wrapped Reports</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 60px;
            animation: fadeIn 1s ease-in;
        }}
        
        header h1 {{
            font-size: 4rem;
            font-weight: 900;
            background: linear-gradient(45deg, #fff, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .year-section {{
            margin-bottom: 50px;
            animation: slideIn 0.8s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(-20px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        
        .year-header {{
            display: flex;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid rgba(255, 255, 255, 0.3);
        }}
        
        .year-header h2 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-right: 20px;
        }}
        
        .year-header .count {{
            background: rgba(255, 255, 255, 0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 1rem;
            font-weight: 600;
        }}
        
        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .report-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            transition: all 0.3s ease;
            border: 2px solid rgba(255, 255, 255, 0.2);
            text-decoration: none;
            color: white;
            display: block;
        }}
        
        .report-card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.5);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}
        
        .report-card.featured {{
            grid-column: span 2;
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(139, 92, 246, 0.3));
            border: 2px solid rgba(167, 139, 250, 0.5);
        }}
        
        .report-card.featured:hover {{
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.4), rgba(139, 92, 246, 0.4));
            border-color: rgba(167, 139, 250, 0.7);
        }}
        
        .report-card h3 {{
            font-size: 1.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .report-card.featured h3 {{
            font-size: 2rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .report-card p {{
            opacity: 0.8;
            font-size: 0.95rem;
        }}
        
        .icon {{
            font-size: 2rem;
            margin-bottom: 10px;
            display: block;
        }}
        
        footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 2px solid rgba(255, 255, 255, 0.2);
            opacity: 0.7;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2.5rem;
            }}
            
            .year-header h2 {{
                font-size: 2rem;
            }}
            
            .report-card.featured {{
                grid-column: span 1;
            }}
            
            .reports-grid {{
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎬 Plex Wrapped</h1>
            <p>Your year in streaming, beautifully wrapped</p>
        </header>
        
        <main>{year_sections_html}
        </main>
        
        <footer>
            <p>Generated by Plex Wrapped Report Generator</p>
            <p>Powered by Tautulli API</p>
        </footer>
    </div>
</body>
</html>
'''
    
    return html_content


def update_index():
    """Main function to update index.html"""
    print("🔄 Updating index.html...")
    
    # Scan for reports
    reports_by_year = scan_wrapped_reports()
    
    if not reports_by_year:
        print("⚠️  No reports found in wrapped_reports directory")
        return
    
    total_reports = sum(len(reports) for reports in reports_by_year.values())
    print(f"📊 Found {total_reports} reports across {len(reports_by_year)} year(s)")
    
    # Generate HTML
    html_content = generate_index_html(reports_by_year)
    
    # Write to file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ index.html updated successfully!")


if __name__ == "__main__":
    update_index()
