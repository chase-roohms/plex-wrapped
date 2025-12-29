"""Update index.html with dynamically generated list of wrapped reports"""
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def scan_wrapped_reports(reports_dir: str = "wrapped_reports") -> Dict[str, List[Dict[str, str]]]:
    """Scan wrapped_reports directory and organize by year"""
    reports_by_year = defaultdict(lambda: {'yearly': [], 'monthly': defaultdict(list)})
    
    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return {}
    
    # List of month names for scanning
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    
    # Scan for year subdirectories
    for year_dir in sorted(reports_path.iterdir(), reverse=True):
        if not year_dir.is_dir():
            continue
        
        year = year_dir.name
        
        # Scan subdirectories: yearly reports vs month folders
        for subdir in sorted(year_dir.iterdir()):
            if not subdir.is_dir():
                continue
            
            subdir_name = subdir.name.lower()
            
            # Check if this is a month folder
            if subdir_name in months:
                # This is a monthly report folder
                month_files = sorted(subdir.glob("*.html"))
                
                for html_file in month_files:
                    filename = html_file.name
                    name_without_ext = filename.replace(".html", "")
                    
                    # Determine if this is the server summary
                    is_server_summary = "server_summary" in filename.lower()
                    
                    # Remove the month suffix to get the username
                    name = name_without_ext.replace(f"_{subdir_name}", "")
                    
                    reports_by_year[year]['monthly'][subdir_name].append({
                        "name": name,
                        "filename": filename,
                        "path": f"{year}/{subdir_name}/{filename}",
                        "is_server_summary": is_server_summary,
                        "month": subdir_name.capitalize()
                    })
        
        # Scan yearly reports (HTML files directly in year directory)
        html_files = sorted(year_dir.glob("*.html"))
        for html_file in html_files:
            filename = html_file.name
            name_without_ext = filename.replace(".html", "")
            
            # Remove any year suffix if it exists (for backwards compatibility)
            if name_without_ext.endswith(f"_{year}"):
                name = name_without_ext.replace(f"_{year}", "")
            else:
                name = name_without_ext
            
            # Determine if this is the server summary
            is_server_summary = "server_summary" in filename.lower()
            
            # This is a yearly report
            reports_by_year[year]['yearly'].append({
                "name": name,
                "filename": filename,
                "path": f"{year}/{filename}",
                "is_server_summary": is_server_summary
            })
    
    # Sort reports within each category
    for year in reports_by_year:
        # Sort yearly reports: server summary first, then alphabetically
        reports_by_year[year]['yearly'].sort(key=lambda x: (not x["is_server_summary"], x["name"].lower()))
        
        # Sort monthly reports within each month
        for month in reports_by_year[year]['monthly']:
            reports_by_year[year]['monthly'][month].sort(key=lambda x: (not x["is_server_summary"], x["name"].lower()))
    
    return dict(reports_by_year)


def generate_index_html(reports_by_year: Dict[str, Dict]) -> str:
    """Generate the complete index.html content"""
    
    # Build year sections HTML
    year_sections_html = ""
    
    for year, report_data in reports_by_year.items():
        yearly_reports = report_data.get('yearly', [])
        monthly_reports = report_data.get('monthly', {})
        
        # Count reports
        yearly_count = len(yearly_reports)
        monthly_count = sum(len(reports) for reports in monthly_reports.values())
        
        # Build yearly report cards HTML
        yearly_cards_html = ""
        
        for report in yearly_reports:
            if report["is_server_summary"]:
                # Featured server summary card
                yearly_cards_html += f'''
                    <!-- Featured: Server Summary -->
                    <a href="wrapped_reports/{report["path"]}" class="report-card featured">
                        <span class="icon">🌟</span>
                        <h3>Server Summary</h3>
                        <p>Complete overview of all server activity</p>
                    </a>
'''
            else:
                # Regular user report card
                yearly_cards_html += f'''
                    <a href="wrapped_reports/{report["path"]}" class="report-card">
                        <span class="icon">👤</span>
                        <h3>{report["name"]}</h3>
                        <p>Yearly wrapped report</p>
                    </a>
'''
        
        # Build monthly reports section if any exist
        monthly_section_html = ""
        if monthly_reports:
            # Order months chronologically
            month_order = ['january', 'february', 'march', 'april', 'may', 'june', 
                          'july', 'august', 'september', 'october', 'november', 'december']
            
            for month_key in reversed(month_order):  # Most recent month first
                if month_key not in monthly_reports:
                    continue
                
                month_reports = monthly_reports[month_key]
                month_name = month_key.capitalize()
                
                # Build cards for this month
                month_cards_html = ""
                for report in month_reports:
                    if report["is_server_summary"]:
                        month_cards_html += f'''
                        <a href="wrapped_reports/{report["path"]}" class="report-card monthly featured">
                            <span class="icon">🌟</span>
                            <h3>Server Summary</h3>
                            <p>{month_name} overview</p>
                        </a>
'''
                    else:
                        month_cards_html += f'''
                        <a href="wrapped_reports/{report["path"]}" class="report-card monthly">
                            <span class="icon">📅</span>
                            <h3>{report["name"]}</h3>
                            <p>{month_name} report</p>
                        </a>
'''
                
                monthly_section_html += f'''
                <div class="monthly-section">
                    <button class="month-toggle" onclick="toggleMonth(this)">
                        <span class="toggle-icon">▶</span>
                        <h3>{month_name}</h3>
                        <span class="count">{len(month_reports)} Report{"s" if len(month_reports) != 1 else ""}</span>
                    </button>
                    <div class="month-content" style="display: none;">
                        <div class="reports-grid">{month_cards_html}
                        </div>
                    </div>
                </div>
'''
        
        # Build year section
        yearly_section = ""
        if yearly_cards_html:
            yearly_section = f'''
                <div class="reports-grid">{yearly_cards_html}
                </div>
'''
        
        year_sections_html += f'''
            <!-- {year} Reports -->
            <div class="year-section">
                <div class="year-header">
                    <h2>{year}</h2>
                    <span class="count">{yearly_count} Yearly{", " + str(monthly_count) + " Monthly" if monthly_count > 0 else ""}</span>
                </div>
                {yearly_section}{monthly_section_html}
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
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🎬</text></svg>">
    
    <!-- Open Graph / Social Media Meta Tags -->
    <meta property="og:title" content="Plex Wrapped Reports">
    <meta property="og:description" content="View personalized Plex viewing statistics and wrapped reports for all users.">
    <meta property="og:type" content="website">
    <meta property="og:image" content="images/plex.png">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Plex Wrapped Reports">
    <meta name="twitter:description" content="View personalized Plex viewing statistics and wrapped reports for all users.">
    <meta name="twitter:image" content="images/plex.png">
    
    <!-- External CSS -->
    <link rel="stylesheet" href="styles/base.css">
    <link rel="stylesheet" href="styles/index.css">
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
    
    <script>
        function toggleMonth(button) {{
            const content = button.nextElementSibling;
            const isActive = button.classList.contains('active');
            
            if (isActive) {{
                button.classList.remove('active');
                content.style.display = 'none';
            }} else {{
                button.classList.add('active');
                content.style.display = 'block';
            }}
        }}
    </script>
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
    
    # Calculate total reports correctly with new structure
    total_reports = 0
    for year_data in reports_by_year.values():
        total_reports += len(year_data.get('yearly', []))
        for monthly_list in year_data.get('monthly', {}).values():
            total_reports += len(monthly_list)
    
    print(f"📊 Found {total_reports} reports across {len(reports_by_year)} year(s)")
    
    # Generate HTML
    html_content = generate_index_html(reports_by_year)
    
    # Write to file
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✅ index.html updated successfully!")


if __name__ == "__main__":
    update_index()
