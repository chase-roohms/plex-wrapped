"""HTML Report Generator - Create beautiful wrapped reports"""
from typing import Dict, List, Any
import os
import json


class WrappedHTMLGenerator:
    """Generate beautiful HTML reports for Plex Wrapped"""
    
    def __init__(self, output_dir: str = 'wrapped_reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_user_report(self, user: str, stats: Dict[str, Any], 
                            period_label: str, user_thumb: str = None, is_server_summary: bool = False, 
                            period_type: str = 'yearly') -> str:
        """Generate a complete wrapped report for a user or server summary"""
        
        # Add favicon link if user_thumb is provided
        favicon_html = ""
        if user_thumb:
            favicon_html = f'\n    <link rel="icon" type="image/png" href="{user_thumb}">'
        
        # Calculate relative path to styles based on report location
        # Monthly reports: 2025/november/user_november.html -> ../../../styles/
        # Yearly reports: 2025/user_2025.html -> ../../styles/
        styles_path = "../../../styles" if period_type == 'monthly' else "../../styles"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>{user}'s Plex Wrapped {period_label}</title>{favicon_html}
    
    <!-- Open Graph / Social Media Meta Tags -->
    <meta property="og:title" content="{user}'s Plex Wrapped {period_label}">
    <meta property="og:description" content="Check out {user}'s Plex viewing stats for {period_label}!">
    <meta property="og:image" content="images/plex.png">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="images/plex.png">
    
    <!-- External CSS -->
    <link rel="stylesheet" href="{styles_path}/base.css">
    <link rel="stylesheet" href="{styles_path}/report.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        
        <!-- Hero Section -->
        <div class="section hero">
            <h1>✨ {'Server' if is_server_summary else user + "'s"} Plex Wrapped</h1>
            <h2>{period_label}</h2>
            <div class="scroll-indicator">↓ Scroll Down ↓</div>
        </div>
        
        <!-- Total Watch Time -->
        <div class="section">
            <div class="stat-card">
                <h3>{'Total Server Watch Time' if is_server_summary else 'Your Total Watch Time'}</h3>
                <div class="big-number">{stats.get('total_hours', 0)} hours</div>
                <div class="subtitle">That's {stats.get('total_days', 0)} days of entertainment!</div>
                <div class="subtitle">{'The server watched' if is_server_summary else 'You watched'} {stats.get('movie_hours', 0)} hours of movies and {stats.get('show_hours', 0)} hours of TV shows</div>
                {self._generate_item_counts(stats)}
            </div>
        </div>
        
        <!-- Ranking -->
        {'' if is_server_summary else self._generate_ranking_section(stats.get('ranking', {}))}
        
        <!-- Most Watched -->
        {self._generate_most_watched_section(stats.get('top_watched', []), period_type)}
        
        <!-- Peak Hours -->
        {self._generate_peak_hours_section(stats.get('peak_hours', {}), is_server_summary)}
        
        <!-- Platform Breakdown -->
        {self._generate_platform_section(stats.get('platforms', {}), is_server_summary)}
        
        <!-- Watch Streak -->
        {self._generate_streak_section(stats.get('streak', {}), is_server_summary)}
        
        <!-- Binge Sessions -->
        {self._generate_binge_section(stats.get('binge_sessions', []), is_server_summary)}
        
        <!-- Genre Diversity -->
        {self._generate_genre_section(stats.get('genres', {}), is_server_summary)}
        
        <!-- Library Coverage -->
        {self._generate_library_section(stats.get('library_coverage', {}), is_server_summary)}
        
        <!-- Library Statistics (Server Summary Only) -->
        {self._generate_library_stats_section(stats) if is_server_summary else ''}
        
        <!-- Unique Content -->
        {'' if is_server_summary else self._generate_unique_content_section(stats.get('unique_content', {}))}
        
        <!-- First and Last -->
        {self._generate_first_last_section(stats.get('first_last', {}))}
        
        <!-- Footer -->
        <div class="section" style="min-height: 50vh;">
            <div class="stat-card" style="text-align: center;">
                <h3>Thanks for watching! 🎉</h3>
                <p class="subtitle">Here's to another great year of entertainment</p>
                <div class="emoji">🍿 📺 🎬</div>
            </div>
        </div>
        
    </div>
    
    <script>
        // Convert times from server timezone (America/Chicago) to user's local timezone
        (function() {{
            const serverTz = 'America/Chicago';
            
            // Convert peak hour display
            const peakDisplay = document.getElementById('peak-time-display');
            if (peakDisplay) {{
                const serverHour = parseInt(peakDisplay.dataset.serverHour);
                
                // Create date in server timezone
                const now = new Date();
                const serverDate = new Date(now.toLocaleString('en-US', {{ timeZone: serverTz }}));
                serverDate.setHours(serverHour, 0, 0, 0);
                
                // Get UTC offset difference
                const serverTime = new Date(serverDate.toLocaleString('en-US', {{ timeZone: serverTz }}));
                const localTime = new Date(serverDate.toLocaleString('en-US', {{ timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone }}));
                const offsetHours = Math.round((localTime - serverTime) / (1000 * 60 * 60));
                
                // Calculate local hour
                let localHour = (serverHour + offsetHours + 24) % 24;
                
                // Format time
                const timeStr = localHour.toString().padStart(2, '0') + ':00';
                const tzAbbr = new Date().toLocaleTimeString('en-US', {{ 
                    timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    timeZoneName: 'short' 
                }}).split(' ')[2] || '';
                
                document.getElementById('peak-hour-time').textContent = timeStr;
                document.getElementById('peak-hour-tz').textContent = tzAbbr;
            }}
            
            // Convert heatmap cell labels
            const heatmap = document.getElementById('hours-heatmap');
            if (heatmap) {{
                const cells = heatmap.querySelectorAll('.heatmap-cell');
                
                // Calculate timezone offset
                const now = new Date();
                const serverDate = new Date(now.toLocaleString('en-US', {{ timeZone: serverTz }}));
                const localDate = new Date(now.toLocaleString('en-US', {{ timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone }}));
                const offsetHours = Math.round((localDate - serverDate) / (1000 * 60 * 60));
                
                cells.forEach(cell => {{
                    const serverHour = parseInt(cell.dataset.hour);
                    const localHour = (serverHour + offsetHours + 24) % 24;
                    const timeStr = localHour.toString().padStart(2, '0') + ':00';
                    cell.textContent = timeStr;
                    
                    // Update tooltip
                    const title = cell.getAttribute('title');
                    if (title) {{
                        const newTitle = title.replace(/\\d+:00/, timeStr);
                        cell.setAttribute('title', newTitle);
                    }}
                }});
            }}
        }})();
    </script>
</body>
</html>"""
        
        # Save to file in year subdirectory
        # For monthly reports: period_label is "November 2025", save in year/november/ subdirectory
        # For yearly reports: period_label is "2025", use as directory
        if period_type == 'monthly':
            # Extract year and month from "November 2025" format
            parts = period_label.split()
            month = parts[0].lower()
            year = parts[-1]
            month_dir = os.path.join(self.output_dir, year, month)
            os.makedirs(month_dir, exist_ok=True)
            filename = os.path.join(month_dir, f"{user.lower().replace(' ', '_')}_{month}.html")
        else:  # yearly
            year_dir = os.path.join(self.output_dir, period_label)
            os.makedirs(year_dir, exist_ok=True)
            filename = os.path.join(year_dir, f"{user.lower().replace(' ', '_')}_{period_label}.html")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename
    
    def _generate_item_counts(self, stats: Dict[str, Any]) -> str:
        """Generate movie and show count display"""
        movie_count = stats.get('movie_count', 0)
        show_count = stats.get('show_count', 0)
        
        if not movie_count and not show_count:
            return ""
        
        return f'<div class="subtitle" style="margin-top: 15px;">📊 {movie_count} movies and {show_count} TV shows</div>'
    
    def _generate_ranking_section(self, ranking: Dict[str, Any]) -> str:
        """Generate ranking section HTML"""
        if not ranking:
            return ""
        
        return f"""
        <div class="section">
            <div class="stat-card" style="text-align: center;">
                <h3>Your Server Ranking</h3>
                <div class="ranking">#{ranking.get('rank', '?')}</div>
                <div class="badge">{ranking.get('callout', 'Great Viewer')}</div>
                <div class="subtitle">Out of {ranking.get('total_users', '?')} users</div>
            </div>
        </div>
        """
    
    def _generate_most_watched_section(self, top_watched: List[Dict[str, Any]], period_type: str = 'yearly') -> str:
        """Generate most watched section with poster images"""
        if not top_watched:
            return ""
        
        # Calculate relative path to thumbnails based on report location
        # Monthly reports: 2025/november/user_november.html -> ../../../thumbnails/
        # Yearly reports: 2025/user_2025.html -> ../../thumbnails/
        thumbnails_path = "../../../thumbnails" if period_type == 'monthly' else "../../thumbnails"
        
        items_html = ""
        for i, item in enumerate(top_watched, 1):
            # Get thumbnail filename from path
            thumbnail_path = item.get('thumbnail', '')
            has_thumbnail = False
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    # Verify it's a real image
                    from PIL import Image as PILImage
                    test_img = PILImage.open(thumbnail_path)
                    if test_img.size[0] > 100:  # Real images are larger than placeholders
                        has_thumbnail = True
                except Exception as e:
                    print(f"Error checking image: {e}")
            
            # Show poster or placeholder icon
            image_html = ""
            if has_thumbnail:
                # Get just the filename from the full path
                thumbnail_filename = os.path.basename(thumbnail_path)
                image_html = f'<img src="{thumbnails_path}/{thumbnail_filename}" style="width: 80px; height: 120px; border-radius: 8px; margin: 0 15px; object-fit: cover;" alt="{item.get("title", "")}">'
            else:
                # Use a nice icon instead of gray box
                image_html = '<div style="width: 80px; height: 120px; background: linear-gradient(135deg, #2a5298, #7e22ce); border-radius: 8px; margin: 0 15px; display: flex; align-items: center; justify-content: center; font-size: 2rem;">🎬</div>'
            
            items_html += f"""
            <div style="display: flex; align-items: center; margin: 15px 0; background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 10px;">
                <div style="font-size: 1.5rem; font-weight: 900; color: #fbbf24; width: 40px; text-align: center;">{i}</div>
                {image_html}
                <div style="flex: 1;">
                    <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 5px;">{item.get('title', 'Unknown')}</div>
                    <div style="color: #fbbf24; font-weight: 700; font-size: 1rem;">{item.get('hours', 0)} hours</div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>Most Watched 🎬</h3>
                <div class="subtitle">Your top {len(top_watched)} most watched titles</div>
                <div style="margin-top: 20px;">
                    {items_html}
                </div>
            </div>
        </div>
        """
    
    def _generate_peak_hours_section(self, peak_hours: Dict[str, Any], is_server_summary: bool = False) -> str:
        """Generate peak hours heatmap section"""
        if not peak_hours:
            return ""
        
        hourly_data = peak_hours.get('hourly_data', [0]*24)
        max_val = max(hourly_data) if hourly_data else 1
        peak_hour = peak_hours.get('peak_hour', 0)
        
        # Create heatmap cells with server timezone data
        cells = ""
        for hour, value in enumerate(hourly_data):
            intensity = (value / max_val) if max_val > 0 else 0
            opacity = 0.3 + (intensity * 0.7)
            cells += f'<div class="heatmap-cell" data-hour="{hour}" style="background: rgba(167, 139, 250, {opacity});" title="{hour}:00 - {value//3600}h">{hour:02d}:00</div>'
        
        distribution = peak_hours.get('distribution', {})
        
        peak_label = 'Peak watching hour' if is_server_summary else 'Your peak watching hour'
        section_title = 'Peak Watching Times' if is_server_summary else 'When You Watch'
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>{section_title}</h3>
                <div class="subtitle" id="peak-time-display" data-server-hour="{peak_hour}" data-server-tz="America/Chicago">{peak_label}: <span id="peak-hour-time">{peak_hours.get('peak_hour_formatted', 'Unknown')}</span> <span id="peak-hour-tz"></span></div>
                <div class="heatmap" id="hours-heatmap">
                    {cells}
                </div>
                <div style="margin-top: 30px;">
                    <div class="list-item">
                        <span class="name">🌅 Morning (6am-12pm)</span>
                        <span class="value">{distribution.get('morning', {}).get('percentage', 0):.1f}%</span>
                    </div>
                    <div class="list-item">
                        <span class="name">☀️ Afternoon (12pm-6pm)</span>
                        <span class="value">{distribution.get('afternoon', {}).get('percentage', 0):.1f}%</span>
                    </div>
                    <div class="list-item">
                        <span class="name">🌆 Evening (6pm-12am)</span>
                        <span class="value">{distribution.get('evening', {}).get('percentage', 0):.1f}%</span>
                    </div>
                    <div class="list-item">
                        <span class="name">🌙 Night (12am-6am)</span>
                        <span class="value">{distribution.get('night', {}).get('percentage', 0):.1f}%</span>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_platform_section(self, platforms: Dict[str, Any], is_server_summary: bool = False) -> str:
        """Generate platform breakdown section"""
        if not platforms or not platforms.get('platforms'):
            return ""
        
        platform_list = platforms.get('platforms', [])[:5]
        items = ""
        
        for platform in platform_list:
            items += f"""
            <div class="list-item">
                <span class="name">{platform.get('name', 'Unknown')}</span>
                <span class="value">{platform.get('hours', 0)} hrs ({platform.get('percentage', 0)}%)</span>
            </div>
            """
        
        top = platforms.get('top_platform', {})
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>{'Most Popular Devices' if is_server_summary else 'Your Favorite Devices'}</h3>
                <div class="subtitle">Top platform: {top.get('name', 'Unknown')} with {top.get('hours', 0)} hours</div>
                {items}
            </div>
        </div>
        """
    
    def _generate_streak_section(self, streak: Dict[str, Any], is_server_summary: bool = False) -> str:
        """Generate watch streak section"""
        if not streak:
            return ""
        
        days_label = 'Days with activity' if is_server_summary else 'You watched on'
        
        return f"""
        <div class="section">
            <div class="stat-card" style="text-align: center;">
                <h3>{'Server Watch Streak' if is_server_summary else 'Your Watch Streak'}</h3>
                <div class="big-number">{streak.get('longest_streak', 0)} days</div>
                <div class="subtitle">Longest streak: {streak.get('streak_start', '')} - {streak.get('streak_end', '')}</div>
                <div class="subtitle">{days_label} {streak.get('total_active_days', 0)} different days</div>
                {f'<div class="badge">🔥 Current streak: {streak.get("current_streak", 0)} days</div>' if streak.get('current_streak', 0) > 0 else ''}
            </div>
        </div>
        """
    
    def _generate_binge_section(self, binge_sessions: List[Dict[str, Any]], is_server_summary: bool = False) -> str:
        """Generate binge sessions section"""
        if not binge_sessions:
            return ""
        
        top_binge = binge_sessions[0]
        items = ""
        
        for i, session in enumerate(binge_sessions[:5], 1):
            items += f"""
            <div class="list-item">
                <span class="name">{i}. {session.get('show', 'Unknown')}</span>
                <span class="value">{session.get('episode_count', 0)} episodes</span>
            </div>
            """
        
        biggest_label = 'Biggest binge' if is_server_summary else 'Your biggest binge'
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>{'Top Binge Sessions' if is_server_summary else 'Epic Binge Sessions'} 🍿</h3>
                <div class="big-number">{top_binge.get('episode_count', 0)} episodes</div>
                <div class="subtitle">{biggest_label}: {top_binge.get('show', 'Unknown')} on {top_binge.get('date', 'Unknown')}</div>
                {items}
            </div>
        </div>
        """
    
    def _generate_genre_section(self, genres: Dict[str, Any], is_server_summary: bool = False) -> str:
        """Generate genre diversity section"""
        if not genres:
            return ""
        
        items = ""
        for genre in genres.get('top_genres', []):
            items += f"""
            <div class="list-item">
                <span class="name">{genre.get('name', 'Unknown')}</span>
                <span class="value">{genre.get('hours', 0)} hrs</span>
            </div>
            """
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>{'Genre Breakdown' if is_server_summary else 'Genre Explorer'}</h3>
                <div class="big-number">{genres.get('unique_genres', 0)}</div>
                <div class="subtitle">Unique genres {'watched' if is_server_summary else 'explored'}</div>
                <h4 style="margin-top: 20px; color: #a78bfa;">{'Most Popular Genres' if is_server_summary else 'Your Top Genres'}</h4>
                {items}
            </div>
        </div>
        """
    
    def _generate_library_section(self, library_coverage: Dict[str, Any], is_server_summary: bool = False) -> str:
        """Generate library coverage section"""
        if not library_coverage or not library_coverage.get('libraries'):
            return ""
        
        items = ""
        for lib in library_coverage.get('libraries', []):
            items += f"""
            <div style="margin: 15px 0;">
                <div class="list-item" style="border: none; padding: 10px 0;">
                    <span class="name">{lib.get('name', 'Unknown')}</span>
                    <span class="value">{lib.get('percentage', 0)}%</span>
                </div>
                <div style="position: relative;">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {lib.get('percentage', 0)}%;"></div>
                    </div>
                    <div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); color: #ffffff; font-size: 12px; font-weight: 600;">
                        {lib.get('watched', 0)}/{lib.get('total', 0)}
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>Library Explorer</h3>
                <div class="subtitle">How much of each library you've explored</div>
                {items}
            </div>
        </div>
        """
    
    def _generate_unique_content_section(self, unique: Dict[str, Any]) -> str:
        """Generate unique content section"""
        if not unique or unique.get('count', 0) == 0:
            return ""
        
        items = ""
        for item in unique.get('unique_items', [])[:10]:
            items += f'<div class="badge">{item.get("title", "Unknown")}</div>'
        
        return f"""
        <div class="section">
            <div class="stat-card" style="text-align: center;">
                <h3>Content Pioneer 🎯</h3>
                <div class="big-number">{unique.get('count', 0)}</div>
                <div class="subtitle">Unique titles only YOU watched</div>
                <div style="margin-top: 20px;">
                    {items}
                </div>
            </div>
        </div>
        """
    
    def _generate_library_stats_section(self, stats: Dict[str, Any]) -> str:
        """Generate library statistics section (server summary only)"""
        library_movies = stats.get('library_movie_count', 0)
        library_shows = stats.get('library_show_count', 0)
        
        if not library_movies and not library_shows:
            return ""
        
        return f"""
        <div class="section">
            <div class="stat-card" style="text-align: center;">
                <h3>📚 Library Statistics</h3>
                <div class="subtitle" style="font-size: 1.5rem; margin: 20px 0;">Total Content Available</div>
                <div style="display: flex; justify-content: space-around; margin: 30px 0;">
                    <div>
                        <div class="big-number" style="font-size: 3rem;">{library_movies}</div>
                        <div class="subtitle">Movies</div>
                    </div>
                    <div>
                        <div class="big-number" style="font-size: 3rem;">{library_shows}</div>
                        <div class="subtitle">TV Shows</div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_first_last_section(self, first_last: Dict[str, Any]) -> str:
        """Generate first and last watch section"""
        if not first_last:
            return ""
        
        first = first_last.get('first', {})
        last = first_last.get('last', {})
        
        if not first or not last:
            return ""
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <div class="grid-2">
                    <div style="text-align: center;">
                        <h3>First Watch</h3>
                        <div class="emoji">🎬</div>
                        <div class="subtitle">{first.get('title', 'Unknown')}</div>
                        <div class="subtitle">{first.get('date', 'Unknown')}</div>
                    </div>
                    <div style="text-align: center;">
                        <h3>Latest Watch</h3>
                        <div class="emoji">📺</div>
                        <div class="subtitle">{last.get('title', 'Unknown')}</div>
                        <div class="subtitle">{last.get('date', 'Unknown')}</div>
                    </div>
                </div>
            </div>
        </div>
        """
