"""Analytics Engine - Compute all wrapped statistics"""
from typing import Dict, List, Tuple, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import requests
import os
from PIL import Image


class WrappedAnalytics:
    """Compute Spotify Wrapped-style statistics from Tautulli data"""
    
    def __init__(self, client):
        self.client = client
        self.thumbnail_dir = 'thumbnails'
        os.makedirs(self.thumbnail_dir, exist_ok=True)
        
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format seconds into human readable duration"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def get_peak_watching_hours(self, user_id: str = None, time_range: int = 365) -> Dict[str, Any]:
        """Get peak watching hours with hourly breakdown"""
        data = self.client.get_plays_by_hourofday(
            time_range=time_range, 
            y_axis='duration',
            user_id=user_id
        )
        
        hours = data.get('data', {}).get('categories', [])
        series_data = data.get('data', {}).get('series', [])
        
        # Combine all media types
        hourly_totals = [0] * 24
        for series in series_data:
            for i, value in enumerate(series.get('data', [])):
                if i < 24:
                    hourly_totals[i] += value
        
        # Find peak hour
        peak_hour = hourly_totals.index(max(hourly_totals)) if hourly_totals else 0
        peak_value = max(hourly_totals) if hourly_totals else 0
        
        # Calculate time of day distribution
        morning = sum(hourly_totals[6:12])  # 6am-12pm
        afternoon = sum(hourly_totals[12:18])  # 12pm-6pm
        evening = sum(hourly_totals[18:24])  # 6pm-12am
        night = sum(hourly_totals[0:6])  # 12am-6am
        total = sum(hourly_totals)
        
        return {
            'hourly_data': hourly_totals,
            'peak_hour': peak_hour,
            'peak_value': peak_value,
            'peak_hour_formatted': f"{peak_hour:02d}:00",
            'distribution': {
                'morning': {'seconds': morning, 'percentage': (morning/total*100) if total > 0 else 0},
                'afternoon': {'seconds': afternoon, 'percentage': (afternoon/total*100) if total > 0 else 0},
                'evening': {'seconds': evening, 'percentage': (evening/total*100) if total > 0 else 0},
                'night': {'seconds': night, 'percentage': (night/total*100) if total > 0 else 0}
            }
        }
    
    def get_platform_breakdown(self, user_id: str = None, time_range: int = 365) -> Dict[str, Any]:
        """Get platform usage breakdown"""
        data = self.client.get_plays_by_top_10_platforms(
            time_range=time_range,
            y_axis='duration',
            user_id=user_id
        )
        
        platforms = data.get('data', {}).get('categories', [])
        series_data = data.get('data', {}).get('series', [])
        
        platform_totals = defaultdict(int)
        for series in series_data:
            for i, platform in enumerate(platforms):
                if i < len(series.get('data', [])):
                    platform_totals[platform] += series['data'][i]
        
        total = sum(platform_totals.values())
        platform_list = [
            {
                'name': platform,
                'seconds': seconds,
                'hours': round(seconds / 3600, 1),
                'percentage': round((seconds / total * 100), 1) if total > 0 else 0
            }
            for platform, seconds in sorted(platform_totals.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            'platforms': platform_list,
            'top_platform': platform_list[0] if platform_list else None
        }
    
    def get_first_last_watch(self, history_data: List[Dict]) -> Dict[str, Any]:
        """Get first and last watch of the period"""
        if not history_data:
            return {'first': None, 'last': None}
        
        # Sort by date
        sorted_history = sorted(history_data, key=lambda x: x.get('date', 0))
        
        first = sorted_history[0] if sorted_history else None
        last = sorted_history[-1] if sorted_history else None
        
        return {
            'first': {
                'title': first.get('full_title', 'Unknown'),
                'date': datetime.fromtimestamp(first.get('date', 0)).strftime('%B %d, %Y'),
                'type': first.get('media_type', 'unknown')
            } if first else None,
            'last': {
                'title': last.get('full_title', 'Unknown'),
                'date': datetime.fromtimestamp(last.get('date', 0)).strftime('%B %d, %Y'),
                'type': last.get('media_type', 'unknown')
            } if last else None
        }
    
    def calculate_watch_streaks(self, history_data: List[Dict]) -> Dict[str, Any]:
        """Calculate longest watch streak (consecutive days with activity)"""
        if not history_data:
            return {'longest_streak': 0, 'current_streak': 0, 'streak_dates': []}
        
        # Get unique dates
        dates = set()
        for item in history_data:
            date = datetime.fromtimestamp(item.get('date', 0)).date()
            dates.add(date)
        
        sorted_dates = sorted(dates)
        
        if not sorted_dates:
            return {'longest_streak': 0, 'current_streak': 0, 'streak_dates': []}
        
        # Calculate streaks
        longest_streak = 1
        current_streak = 1
        longest_streak_dates = [sorted_dates[0]]
        current_streak_dates = [sorted_dates[0]]
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                current_streak += 1
                current_streak_dates.append(sorted_dates[i])
            else:
                if current_streak > longest_streak:
                    longest_streak = current_streak
                    longest_streak_dates = current_streak_dates.copy()
                current_streak = 1
                current_streak_dates = [sorted_dates[i]]
        
        # Check final streak
        if current_streak > longest_streak:
            longest_streak = current_streak
            longest_streak_dates = current_streak_dates.copy()
        
        # Check if current streak is ongoing
        today = datetime.now().date()
        current_ongoing = (today - sorted_dates[-1]).days <= 1
        
        return {
            'longest_streak': longest_streak,
            'current_streak': current_streak if current_ongoing else 0,
            'streak_start': longest_streak_dates[0].strftime('%B %d'),
            'streak_end': longest_streak_dates[-1].strftime('%B %d'),
            'total_active_days': len(dates)
        }
    
    def detect_binge_sessions(self, history_data: List[Dict]) -> List[Dict[str, Any]]:
        """Detect binge watching sessions (consecutive episodes)"""
        # Group by grandparent (show) and sort by date
        show_watches = defaultdict(list)
        
        for item in history_data:
            if item.get('media_type') == 'episode':
                grandparent = item.get('grandparent_title')
                if grandparent:
                    show_watches[grandparent].append({
                        'date': item.get('date'),
                        'title': item.get('full_title'),
                        'episode_index': item.get('media_index'),
                        'season': item.get('parent_media_index')
                    })
        
        # Detect binge sessions (3+ episodes within 8 hours)
        binge_sessions = []
        
        for show, episodes in show_watches.items():
            if len(episodes) < 3:
                continue
                
            sorted_episodes = sorted(episodes, key=lambda x: x['date'])
            
            # Look for consecutive episodes within time window
            session_episodes = [sorted_episodes[0]]
            
            for i in range(1, len(sorted_episodes)):
                time_diff = sorted_episodes[i]['date'] - session_episodes[-1]['date']
                
                # If within 8 hours, add to session
                if time_diff <= 28800:  # 8 hours in seconds
                    session_episodes.append(sorted_episodes[i])
                else:
                    # End session if 3+ episodes
                    if len(session_episodes) >= 3:
                        binge_sessions.append({
                            'show': show,
                            'episode_count': len(session_episodes),
                            'date': datetime.fromtimestamp(session_episodes[0]['date']).strftime('%B %d, %Y'),
                            'episodes': session_episodes
                        })
                    session_episodes = [sorted_episodes[i]]
            
            # Check final session
            if len(session_episodes) >= 3:
                binge_sessions.append({
                    'show': show,
                    'episode_count': len(session_episodes),
                    'date': datetime.fromtimestamp(session_episodes[0]['date']).strftime('%B %d, %Y'),
                    'episodes': session_episodes
                })
        
        # Sort by episode count
        binge_sessions.sort(key=lambda x: x['episode_count'], reverse=True)
        
        return binge_sessions
    
    def analyze_genre_diversity(self, history_data: List[Dict]) -> Dict[str, Any]:
        """Analyze genre diversity from watched content"""
        all_genres = []
        genre_time = defaultdict(int)
        
        for item in history_data:
            rating_key = item.get('rating_key') or item.get('grandparent_rating_key')
            if not rating_key:
                continue
            
            # Get metadata for genres
            try:
                metadata = self.client.get_metadata(rating_key)
                genres = metadata.get('data', {}).get('genres', [])
                duration = item.get('play_duration', 0)
                
                for genre in genres:
                    all_genres.append(genre)
                    genre_time[genre] += duration
                    
            except Exception as e:
                continue
        
        unique_genres = len(set(all_genres))
        genre_counts = Counter(all_genres)
        
        # Top genres by time
        top_genres = [
            {
                'name': genre,
                'seconds': seconds,
                'hours': round(seconds / 3600, 1)
            }
            for genre, seconds in sorted(genre_time.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        return {
            'unique_genres': unique_genres,
            'top_genres': top_genres,
            'total_genre_tags': len(all_genres)
        }
    
    def calculate_library_coverage(self, history_data: List[Dict]) -> Dict[str, Any]:
        """Calculate what percentage of libraries was explored"""
        # Get all libraries
        libraries_response = self.client.get_libraries()
        libraries = libraries_response.get('data', [])
        
        coverage = []
        
        # First, enrich history with section_id by checking media_type and categorizing
        for library in libraries:
            section_id = library.get('section_id')
            section_name = library.get('section_name')
            section_type = library.get('section_type')
            
            # Get total items in library
            try:
                media_info = self.client.get_library_media_info(section_id, length=100000)
                total_items = media_info.get('data', {}).get('recordsTotal', 0)
                
                # Count unique items watched from this library by matching section_type to media_type
                watched_items = set()
                for item in history_data:
                    media_type = item.get('media_type', '')
                    
                    # Match media types to library types
                    matches = False
                    if section_type == 'movie' and media_type == 'movie':
                        matches = True
                    elif section_type == 'show' and media_type == 'episode':
                        matches = True
                    elif section_type == 'artist' and media_type == 'track':
                        matches = True
                    
                    if matches:
                        # Use grandparent for episodes/tracks, rating_key for movies
                        if media_type in ['episode', 'track']:
                            watched_items.add(item.get('grandparent_rating_key'))
                        else:
                            watched_items.add(item.get('rating_key'))
                
                watched_count = len([x for x in watched_items if x])
                percentage = (watched_count / total_items * 100) if total_items > 0 else 0
                
                coverage.append({
                    'name': section_name,
                    'type': section_type,
                    'watched': watched_count,
                    'total': total_items,
                    'percentage': round(percentage, 1)
                })
            except Exception as e:
                print(f"Error processing library {section_name}: {e}")
                continue
        
        return {'libraries': coverage}
    
    def find_unique_content(self, all_users_history: Dict[str, List[Dict]], 
                           target_user: str) -> Dict[str, Any]:
        """Find content watched only by target user"""
        if target_user not in all_users_history:
            return {'unique_items': []}
        
        # Get all rating keys for target user
        user_items = set()
        user_item_details = {}
        for item in all_users_history[target_user]:
            key = item.get('grandparent_rating_key') or item.get('rating_key')
            if key:
                user_items.add(key)
                if key not in user_item_details:
                    user_item_details[key] = {
                        'title': item.get('grandparent_title') or item.get('title'),
                        'type': item.get('media_type')
                    }
        
        # Get all rating keys for other users
        other_users_items = set()
        for user, history in all_users_history.items():
            if user != target_user:
                for item in history:
                    key = item.get('grandparent_rating_key') or item.get('rating_key')
                    if key:
                        other_users_items.add(key)
        
        # Find unique items
        unique_keys = user_items - other_users_items
        unique_items = [
            user_item_details[key] for key in unique_keys 
            if key in user_item_details
        ]
        
        return {
            'unique_items': unique_items[:10],  # Top 10
            'count': len(unique_items)
        }
    
    def calculate_user_rankings(self, all_users_stats: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """Calculate user rankings with fun callouts"""
        rankings = []
        
        for user, stats in all_users_stats.items():
            if user == 'Total':
                continue
            rankings.append({
                'user': user,
                'total_time': stats.get('total', 0),
                'movie_time': stats.get('movie', 0),
                'episode_time': stats.get('episode', 0)
            })
        
        rankings.sort(key=lambda x: x['total_time'], reverse=True)
        
        # Add ranks and callouts
        callouts = [
            "👑 Server Champion",
            "🥈 Runner-Up Extraordinaire",
            "🥉 Bronze Binger",
            "🎬 Movie Maven",
            "📺 TV Enthusiast",
            "🍿 Popcorn Pro",
            "⭐ Rising Star",
            "🎪 Entertainment Seeker",
            "🎭 Culture Consumer",
            "🎨 Content Connoisseur"
        ]
        
        for i, rank in enumerate(rankings):
            rank['rank'] = i + 1
            rank['callout'] = callouts[i] if i < len(callouts) else "🎯 Dedicated Viewer"
            rank['total_hours'] = round(rank['total_time'] / 3600, 1)
        
        return rankings
    
    def get_top_watched_items(self, history_data: List[Dict], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top watched items with poster images"""
        # Aggregate watch time by item
        item_stats = defaultdict(lambda: {'duration': 0, 'title': '', 'rating_key': None, 'type': ''})
        
        for item in history_data:
            # Use grandparent for episodes, parent for tracks, rating_key for movies
            media_type = item.get('media_type')
            
            if media_type == 'episode':
                key = item.get('grandparent_rating_key')
                title = item.get('grandparent_title')
            elif media_type == 'track':
                key = item.get('grandparent_rating_key')
                title = item.get('grandparent_title')
            else:
                key = item.get('rating_key')
                title = item.get('title')
            
            if key and title:
                item_stats[key]['duration'] += item.get('play_duration', 0)
                item_stats[key]['title'] = title[:36] + '...' if len(title) > 36 else title
                item_stats[key]['rating_key'] = key
                item_stats[key]['type'] = media_type
        
        # Sort by duration and get top items
        sorted_items = sorted(item_stats.items(), key=lambda x: x[1]['duration'], reverse=True)[:limit]
        
        result = []
        for rating_key, stats in sorted_items:
            # Download thumbnail
            thumbnail_path = self._download_thumbnail(stats['rating_key'], stats['title'])
            
            result.append({
                'title': stats['title'],
                'rating_key': stats['rating_key'],
                'duration': stats['duration'],
                'hours': round(stats['duration'] / 3600, 1),
                'thumbnail': thumbnail_path,
                'type': stats['type']
            })
        
        return result
    
    def _download_thumbnail(self, rating_key: int, title: str) -> str:
        """Download thumbnail from Plex server"""
        thumbnail_path = f'{self.thumbnail_dir}/{rating_key}.jpg'
        
        # Return if already exists and is valid
        if os.path.exists(thumbnail_path):
            try:
                # Check if it's a valid image with reasonable size
                img = Image.open(thumbnail_path)
                if img.size[0] > 100:  # Real images are larger
                    return thumbnail_path
            except:
                pass
        
        try:
            # Get the thumbnail URL from Plex
            plex_base_url = self.client.plex_base_url
            plex_token = self.client.plex_token
            
            # Try to get metadata for better thumbnail
            try:
                metadata = self.client.get_metadata(rating_key)
                thumb = metadata.get('data', {}).get('thumb', '')
                if thumb:
                    url = f"{plex_base_url}{thumb}?X-Plex-Token={plex_token}"
                    response = requests.get(url, verify=False, timeout=10)
                    if response.status_code == 200 and len(response.content) > 5000:  # Valid image should be larger
                        with open(thumbnail_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Verify the saved image
                        try:
                            img = Image.open(thumbnail_path)
                            if img.size[0] > 100:
                                return thumbnail_path
                        except:
                            pass
            except Exception as e:
                print(f"    ⚠️  Could not download thumbnail for {title}: {e}")
            
            # If we get here, download failed - don't create placeholder
            # Return empty string so we can skip showing it
            return ""
            
        except Exception as e:
            print(f"    ⚠️  Error downloading thumbnail: {e}")
            return ""
