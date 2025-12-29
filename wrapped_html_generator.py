"""HTML Report Generator - Create beautiful wrapped reports"""
from typing import Dict, List, Any
import os
import json
import base64


class WrappedHTMLGenerator:
    """Generate beautiful HTML reports for Plex Wrapped"""
    
    def __init__(self, output_dir: str = 'wrapped_reports'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_user_report(self, user: str, stats: Dict[str, Any], 
                            period_label: str) -> str:
        """Generate a complete wrapped report for a user"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <title>{user}'s Plex Wrapped {period_label}</title>
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
            overflow-x: hidden;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .section {{
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 40px 20px;
            animation: fadeIn 1s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .hero {{
            text-align: center;
        }}
        
        .hero h1 {{
            font-size: 5rem;
            font-weight: 900;
            background: linear-gradient(45deg, #fff, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            animation: glow 2s ease-in-out infinite alternate;
        }}
        
        @keyframes glow {{
            from {{ text-shadow: 0 0 20px rgba(167, 139, 250, 0.5); }}
            to {{ text-shadow: 0 0 40px rgba(167, 139, 250, 0.8); }}
        }}
        
        .hero h2 {{
            font-size: 2rem;
            margin: 20px 0;
            opacity: 0.9;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            margin: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            width: 100%;
            max-width: 800px;
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card h3 {{
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #a78bfa;
        }}
        
        .big-number {{
            font-size: 4rem;
            font-weight: 900;
            color: #fbbf24;
            margin: 20px 0;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        }}
        
        .subtitle {{
            font-size: 1.2rem;
            opacity: 0.8;
            margin: 10px 0;
        }}
        
        .list-item {{
            background: rgba(255, 255, 255, 0.05);
            padding: 15px 20px;
            margin: 10px 0;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #a78bfa;
        }}
        
        .list-item .name {{
            font-size: 1.1rem;
            font-weight: 600;
        }}
        
        .list-item .value {{
            font-size: 1.1rem;
            color: #fbbf24;
            font-weight: 700;
        }}
        
        .heatmap {{
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 5px;
            margin: 20px 0;
        }}
        
        .heatmap-cell {{
            aspect-ratio: 1;
            background: rgba(167, 139, 250, 0.3);
            border-radius: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            transition: all 0.3s ease;
        }}
        
        .heatmap-cell:hover {{
            transform: scale(1.1);
        }}
        
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #a78bfa, #fbbf24);
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            font-weight: 700;
            transition: width 2s ease;
        }}
        
        .badge {{
            display: inline-block;
            background: linear-gradient(135deg, #fbbf24, #f59e0b);
            color: #1e3c72;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 700;
            font-size: 1.2rem;
            margin: 10px 5px;
            box-shadow: 0 4px 15px rgba(251, 191, 36, 0.3);
        }}
        
        .ranking {{
            font-size: 6rem;
            font-weight: 900;
            color: #fbbf24;
            text-shadow: 3px 3px 15px rgba(0, 0, 0, 0.5);
        }}
        
        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            width: 100%;
            max-width: 1000px;
        }}
        
        .emoji {{
            font-size: 3rem;
            margin: 20px 0;
        }}
        
        @media (max-width: 768px) {{
            .hero h1 {{ font-size: 3rem; }}
            .big-number {{ font-size: 2.5rem; }}
            .ranking {{ font-size: 4rem; }}
            .heatmap {{ grid-template-columns: repeat(6, 1fr); }}
        }}
        
        .scroll-indicator {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            animation: bounce 2s infinite;
            opacity: 0.7;
        }}
        
        @keyframes bounce {{
            0%, 20%, 50%, 80%, 100% {{ transform: translateX(-50%) translateY(0); }}
            40% {{ transform: translateX(-50%) translateY(-10px); }}
            60% {{ transform: translateX(-50%) translateY(-5px); }}
        }}
        
        .chart {{
            width: 100%;
            max-width: 600px;
            margin: 20px auto;
        }}
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div class="container">
        
        <!-- Hero Section -->
        <div class="section hero">
            <h1>✨ {user}'s Plex Wrapped</h1>
            <h2>{period_label}</h2>
            <div class="scroll-indicator">↓ Scroll Down ↓</div>
        </div>
        
        <!-- Total Watch Time -->
        <div class="section">
            <div class="stat-card">
                <h3>Your Total Watch Time</h3>
                <div class="big-number">{stats.get('total_hours', 0)} hours</div>
                <div class="subtitle">That's {stats.get('total_days', 0)} days of entertainment!</div>
                <div class="subtitle">You watched {stats.get('movie_hours', 0)} hours of movies and {stats.get('show_hours', 0)} hours of TV shows</div>
            </div>
        </div>
        
        <!-- Ranking -->
        {self._generate_ranking_section(stats.get('ranking', {}))}
        
        <!-- Most Watched -->
        {self._generate_most_watched_section(stats.get('top_watched', []))}
        
        <!-- Peak Hours -->
        {self._generate_peak_hours_section(stats.get('peak_hours', {}))}
        
        <!-- Platform Breakdown -->
        {self._generate_platform_section(stats.get('platforms', {}))}
        
        <!-- Watch Streak -->
        {self._generate_streak_section(stats.get('streak', {}))}
        
        <!-- Binge Sessions -->
        {self._generate_binge_section(stats.get('binge_sessions', []))}
        
        <!-- Genre Diversity -->
        {self._generate_genre_section(stats.get('genres', {}))}
        
        <!-- Library Coverage -->
        {self._generate_library_section(stats.get('library_coverage', {}))}
        
        <!-- Unique Content -->
        {self._generate_unique_content_section(stats.get('unique_content', {}))}
        
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
</body>
</html>"""
        
        # Save to file in year subdirectory
        year_dir = os.path.join(self.output_dir, period_label)
        os.makedirs(year_dir, exist_ok=True)
        filename = os.path.join(year_dir, f"{user.lower().replace(' ', '_')}_{period_label.lower()}.html")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return filename
    
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
    
    def _generate_most_watched_section(self, top_watched: List[Dict[str, Any]]) -> str:
        """Generate most watched section with poster images"""
        if not top_watched:
            return ""
        
        items_html = ""
        for i, item in enumerate(top_watched, 1):
            # Convert image to base64 for embedding
            img_data = ""
            thumbnail_path = item.get('thumbnail', '')
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    # Verify it's a real image
                    from PIL import Image as PILImage
                    test_img = PILImage.open(thumbnail_path)
                    if test_img.size[0] > 100:  # Real images are larger than placeholders
                        with open(thumbnail_path, 'rb') as f:
                            img_bytes = f.read()
                            img_data = base64.b64encode(img_bytes).decode('utf-8')
                except Exception as e:
                    print(f"Error encoding image: {e}")
            
            # Show poster or placeholder icon
            image_html = ""
            if img_data:
                image_html = f'<img src="data:image/jpeg;base64,{img_data}" style="width: 80px; height: 120px; border-radius: 8px; margin: 0 15px; object-fit: cover;" alt="{item.get("title", "")}">'
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
    
    def _generate_peak_hours_section(self, peak_hours: Dict[str, Any]) -> str:
        """Generate peak hours heatmap section"""
        if not peak_hours:
            return ""
        
        hourly_data = peak_hours.get('hourly_data', [0]*24)
        max_val = max(hourly_data) if hourly_data else 1
        
        # Create heatmap cells
        cells = ""
        for hour, value in enumerate(hourly_data):
            intensity = (value / max_val) if max_val > 0 else 0
            opacity = 0.3 + (intensity * 0.7)
            cells += f'<div class="heatmap-cell" style="background: rgba(167, 139, 250, {opacity});" title="{hour}:00 - {value//3600}h">{hour:02d}:00</div>'
        
        distribution = peak_hours.get('distribution', {})
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>When You Watch</h3>
                <div class="subtitle">Your peak watching hour: {peak_hours.get('peak_hour_formatted', 'Unknown')}</div>
                <div class="heatmap">
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
    
    def _generate_platform_section(self, platforms: Dict[str, Any]) -> str:
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
                <h3>Your Favorite Devices</h3>
                <div class="subtitle">Top platform: {top.get('name', 'Unknown')} with {top.get('hours', 0)} hours</div>
                {items}
            </div>
        </div>
        """
    
    def _generate_streak_section(self, streak: Dict[str, Any]) -> str:
        """Generate watch streak section"""
        if not streak:
            return ""
        
        return f"""
        <div class="section">
            <div class="stat-card" style="text-align: center;">
                <h3>Your Watch Streak</h3>
                <div class="big-number">{streak.get('longest_streak', 0)} days</div>
                <div class="subtitle">Longest streak: {streak.get('streak_start', '')} - {streak.get('streak_end', '')}</div>
                <div class="subtitle">You watched on {streak.get('total_active_days', 0)} different days</div>
                {f'<div class="badge">🔥 Current streak: {streak.get("current_streak", 0)} days</div>' if streak.get('current_streak', 0) > 0 else ''}
            </div>
        </div>
        """
    
    def _generate_binge_section(self, binge_sessions: List[Dict[str, Any]]) -> str:
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
        
        return f"""
        <div class="section">
            <div class="stat-card">
                <h3>Epic Binge Sessions 🍿</h3>
                <div class="big-number">{top_binge.get('episode_count', 0)} episodes</div>
                <div class="subtitle">Your biggest binge: {top_binge.get('show', 'Unknown')} on {top_binge.get('date', 'Unknown')}</div>
                {items}
            </div>
        </div>
        """
    
    def _generate_genre_section(self, genres: Dict[str, Any]) -> str:
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
                <h3>Genre Explorer</h3>
                <div class="big-number">{genres.get('unique_genres', 0)}</div>
                <div class="subtitle">Unique genres explored</div>
                <h4 style="margin-top: 20px; color: #a78bfa;">Your Top Genres</h4>
                {items}
            </div>
        </div>
        """
    
    def _generate_library_section(self, library_coverage: Dict[str, Any]) -> str:
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
