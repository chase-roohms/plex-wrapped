"""Plex Wrapped Report Generator - Main Script"""
import os
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Literal, Dict, List, Any
from collections import defaultdict

from tautulli_client import TautulliClient
from wrapped_analytics import WrappedAnalytics
from wrapped_html_generator import WrappedHTMLGenerator
from definitions import tracked_media


def get_date_range(period_type: Literal['monthly', 'yearly'] = 'monthly'):
    """Get date range for the analysis period"""
    today = date.today() + timedelta(days=1)
    if period_type == 'monthly':
        first_day_current_month = today.replace(day=1)
        first = (first_day_current_month - relativedelta(months=1))
        last = (first_day_current_month - relativedelta(days=1))
    else:  # yearly
        first_day_current_year = today.replace(month=1, day=1)
        first = first_day_current_year
        last = today
    return first, last


def generate_wrapped_reports(period: Literal['monthly', 'yearly'] = 'yearly'):
    """Generate Plex Wrapped reports for all users"""
    
    print("🎬 Starting Plex Wrapped Report Generation...")
    print("=" * 60)
    
    # Initialize clients
    client = TautulliClient()
    analytics = WrappedAnalytics(client)
    html_generator = WrappedHTMLGenerator()
    
    # Get date range
    first, last = get_date_range(period)
    first_str = first.strftime("%Y-%m-%d")
    last_str = last.strftime("%Y-%m-%d")
    period_label = first.strftime('%B') if period == 'monthly' else str(first.year)
    
    print(f"📅 Period: {first_str} to {last_str}")
    print(f"🏷️  Label: {period_label}")
    
    # Calculate time range in days for API calls
    time_range = (last - first).days
    
    # Get all history
    print("\n📊 Fetching watch history...")
    history_response = client.get_history(after=first_str, before=last_str, length=10000)
    # The response has a nested 'data' object with actual data in it
    data_object = history_response.get('data', {})
    all_history = data_object.get('data', []) if isinstance(data_object, dict) else []
    print(f"✅ Retrieved {len(all_history)} history entries")
    
    # Organize history by user
    user_history = defaultdict(list)
    user_stats = {}
    user_ids = {}  # Track user_id for each user
    
    for entry in all_history:
        user = entry.get('friendly_name')
        media_type = entry.get('media_type')
        user_id = entry.get('user_id')
        
        if media_type in tracked_media and user:
            user_history[user].append(entry)
            
            # Store the user_id for this user
            if user not in user_ids and user_id:
                user_ids[user] = user_id
            
            if user not in user_stats:
                user_stats[user] = {'movie': 0, 'episode': 0, 'total': 0}
            
            duration = entry.get('play_duration', 0)
            user_stats[user][media_type] += duration
            user_stats[user]['total'] += duration
    
    print(f"\n👥 Found {len(user_history)} users")
    
    # Calculate rankings
    print("\n🏆 Calculating user rankings...")
    rankings = analytics.calculate_user_rankings(user_stats)
    
    # Generate reports for each user
    print("\n📝 Generating individual user reports...")
    generated_files = []
    
    for user, history in user_history.items():
        print(f"\n  Processing: {user}")
        
        # Get user's stats
        user_stat = user_stats.get(user, {})
        total_seconds = user_stat.get('total', 0)
        movie_seconds = user_stat.get('movie', 0)
        episode_seconds = user_stat.get('episode', 0)
        
        # Find user's ranking
        user_ranking = next((r for r in rankings if r['user'] == user), None)
        
        # Collect all statistics
        wrapped_stats = {
            'total_hours': round(total_seconds / 3600, 1),
            'total_days': round(total_seconds / 86400, 1),
            'movie_hours': round(movie_seconds / 3600, 1),
            'show_hours': round(episode_seconds / 3600, 1),
            'ranking': {
                'rank': user_ranking['rank'] if user_ranking else None,
                'callout': user_ranking['callout'] if user_ranking else None,
                'total_users': len(rankings)
            }
        }
        
        # Get top watched items with posters
        try:
            print("    - Finding top watched items...")
            top_watched = analytics.get_top_watched_items(history, limit=5)
            wrapped_stats['top_watched'] = top_watched
        except Exception as e:
            print(f"    ⚠️  Error getting top watched: {e}")
            wrapped_stats['top_watched'] = []
        
        # Peak watching hours
        try:
            print("    - Analyzing peak hours...")
            peak_hours = analytics.get_peak_watching_hours(
                user_id=str(history[0].get('user_id')),
                time_range=time_range
            )
            wrapped_stats['peak_hours'] = peak_hours
        except Exception as e:
            print(f"    ⚠️  Error getting peak hours: {e}")
            wrapped_stats['peak_hours'] = {}
        
        # Platform breakdown
        try:
            print("    - Analyzing platforms...")
            platforms = analytics.get_platform_breakdown(
                user_id=str(history[0].get('user_id')),
                time_range=time_range
            )
            wrapped_stats['platforms'] = platforms
        except Exception as e:
            print(f"    ⚠️  Error getting platforms: {e}")
            wrapped_stats['platforms'] = {}
        
        # First and last watch
        try:
            print("    - Finding first/last watches...")
            first_last = analytics.get_first_last_watch(history)
            wrapped_stats['first_last'] = first_last
        except Exception as e:
            print(f"    ⚠️  Error getting first/last: {e}")
            wrapped_stats['first_last'] = {}
        
        # Watch streaks
        try:
            print("    - Calculating watch streaks...")
            streak = analytics.calculate_watch_streaks(history)
            wrapped_stats['streak'] = streak
        except Exception as e:
            print(f"    ⚠️  Error calculating streaks: {e}")
            wrapped_stats['streak'] = {}
        
        # Binge sessions
        try:
            print("    - Detecting binge sessions...")
            binge_sessions = analytics.detect_binge_sessions(history)
            wrapped_stats['binge_sessions'] = binge_sessions
        except Exception as e:
            print(f"    ⚠️  Error detecting binges: {e}")
            wrapped_stats['binge_sessions'] = []
        
        # Genre diversity (may be slow due to API calls)
        try:
            print("    - Analyzing genre diversity (this may take a moment)...")
            genres = analytics.analyze_genre_diversity(history[:100])  # Limit to first 100 for performance
            wrapped_stats['genres'] = genres
        except Exception as e:
            print(f"    ⚠️  Error analyzing genres: {e}")
            wrapped_stats['genres'] = {}
        
        # Library coverage
        try:
            print("    - Calculating library coverage...")
            library_coverage = analytics.calculate_library_coverage(history)
            wrapped_stats['library_coverage'] = library_coverage
        except Exception as e:
            print(f"    ⚠️  Error calculating coverage: {e}")
            wrapped_stats['library_coverage'] = {}
        
        # Unique content
        try:
            print("    - Finding unique content...")
            unique_content = analytics.find_unique_content(dict(user_history), user)
            wrapped_stats['unique_content'] = unique_content
        except Exception as e:
            print(f"    ⚠️  Error finding unique content: {e}")
            wrapped_stats['unique_content'] = {}
        
        # Generate HTML report
        try:
            print("    - Generating HTML report...")
            # Get user profile picture
            user_thumb = None
            if user in user_ids:
                try:
                    user_data = client.get_user(user_ids[user])
                    user_info = user_data.get('data', {})
                    user_thumb = user_info.get('user_thumb')
                except Exception as e:
                    print(f"    ⚠️  Could not fetch user profile picture: {e}")
            
            filename = html_generator.generate_user_report(user, wrapped_stats, period_label, user_thumb)
            generated_files.append(filename)
            print(f"    ✅ Report saved: {filename}")
        except Exception as e:
            print(f"    ❌ Error generating report: {e}")
    
    # Generate summary report
    print("\n📊 Generating server summary report...")
    try:
        summary_stats = {
            'total_hours': round(sum(s.get('total', 0) for s in user_stats.values()) / 3600, 1),
            'total_days': round(sum(s.get('total', 0) for s in user_stats.values()) / 86400, 1),
            'movie_hours': round(sum(s.get('movie', 0) for s in user_stats.values()) / 3600, 1),
            'show_hours': round(sum(s.get('episode', 0) for s in user_stats.values()) / 3600, 1),
            'ranking': {
                'rank': 1,
                'callout': '🌟 Server Overview',
                'total_users': len(rankings)
            }
        }
        
        # Aggregate all history for server-wide stats
        peak_hours = analytics.get_peak_watching_hours(time_range=time_range)
        platforms = analytics.get_platform_breakdown(time_range=time_range)
        first_last = analytics.get_first_last_watch(all_history)
        streak = analytics.calculate_watch_streaks(all_history)
        binge_sessions = analytics.detect_binge_sessions(all_history)
        
        summary_stats.update({
            'peak_hours': peak_hours,
            'platforms': platforms,
            'first_last': first_last,
            'streak': streak,
            'binge_sessions': binge_sessions,
            'genres': {},
            'library_coverage': {},
            'unique_content': {}
        })
        
        filename = html_generator.generate_user_report('Server Summary', summary_stats, period_label)
        generated_files.append(filename)
        print(f"✅ Summary report saved: {filename}")
    except Exception as e:
        print(f"❌ Error generating summary: {e}")
    
    # Print completion summary
    print("\n" + "=" * 60)
    print("🎉 Plex Wrapped Report Generation Complete!")
    print(f"📁 Generated {len(generated_files)} reports")
    print(f"📂 Location: {html_generator.output_dir}")
    print("\n📋 Generated Files:")
    for f in generated_files:
        print(f"   - {os.path.basename(f)}")
    print("\n💡 Open these HTML files in your browser to view!")
    print("=" * 60)


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Plex Wrapped reports')
    parser.add_argument('--period', type=str, choices=['monthly', 'yearly'], 
                       default='yearly', help='Report period (monthly or yearly)')
    
    args = parser.parse_args()
    
    generate_wrapped_reports(period=args.period)
