"""
One-time migration script to organize existing reports into year subdirectories
"""
import os
import shutil
from pathlib import Path


def migrate_reports():
    """Move existing reports from wrapped_reports/ to wrapped_reports/YEAR/"""
    reports_dir = Path("wrapped_reports")
    
    if not reports_dir.exists():
        print("❌ wrapped_reports directory not found")
        return
    
    # Find all HTML files in the root of wrapped_reports
    html_files = list(reports_dir.glob("*.html"))
    
    if not html_files:
        print("✅ No reports to migrate (or already migrated)")
        return
    
    print(f"📦 Found {len(html_files)} reports to migrate")
    
    moved_count = 0
    for html_file in html_files:
        # Extract year from filename (e.g., user_2025.html -> 2025)
        filename = html_file.name
        
        # Find year in filename
        parts = filename.replace('.html', '').split('_')
        year = None
        for part in parts:
            if part.isdigit() and len(part) == 4:
                year = part
                break
        
        if not year:
            print(f"⚠️  Skipping {filename} - couldn't determine year")
            continue
        
        # Create year subdirectory
        year_dir = reports_dir / year
        year_dir.mkdir(exist_ok=True)
        
        # Move file
        destination = year_dir / filename
        shutil.move(str(html_file), str(destination))
        print(f"  ✅ Moved {filename} → {year}/{filename}")
        moved_count += 1
    
    print(f"\n🎉 Migration complete! Moved {moved_count} reports")
    print("💡 Now run: python update_index.py")


if __name__ == "__main__":
    migrate_reports()
