"""Tautulli API Client - Centralized API calls"""
import os
import requests
import json
import urllib3
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Disable SSL warnings if using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()


class TautulliClient:
    """Client for interacting with Tautulli API"""
    
    def __init__(self):
        self.base_url = os.getenv('TAUTULLI_URL') + '/api/v2'
        self.plex_base_url = os.getenv('PLEX_URL')
        self.apikey = os.getenv('TAUTULLI_API_KEY')
        self.plex_token = os.getenv('PLEX_API_KEY')
        
    def _make_request(self, cmd: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Tautulli API"""
        url_params = {'apikey': self.apikey, 'cmd': cmd}
        if params:
            url_params.update(params)
        
        response = requests.get(self.base_url, params=url_params, verify=False)
        response.raise_for_status()
        return json.loads(response.text).get('response', {})
    
    def get_history(self, after: str = None, before: str = None, 
                    length: int = 10000, grouping: int = 0,
                    user_id: int = None) -> Dict[str, Any]:
        """Get history from Tautulli"""
        params = {'length': length, 'grouping': grouping}
        if after:
            params['after'] = after
        if before:
            params['before'] = before
        if user_id:
            params['user_id'] = user_id
        return self._make_request('get_history', params)
    
    def get_plays_by_hourofday(self, time_range: int = 30, 
                                y_axis: str = 'plays',
                                user_id: str = None,
                                grouping: int = 0) -> Dict[str, Any]:
        """Get plays by hour of day"""
        params = {'time_range': time_range, 'y_axis': y_axis, 'grouping': grouping}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('get_plays_by_hourofday', params)
    
    def get_plays_by_dayofweek(self, time_range: int = 30,
                                y_axis: str = 'plays',
                                user_id: str = None,
                                grouping: int = 0) -> Dict[str, Any]:
        """Get plays by day of week"""
        params = {'time_range': time_range, 'y_axis': y_axis, 'grouping': grouping}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('get_plays_by_dayofweek', params)
    
    def get_plays_by_top_10_platforms(self, time_range: int = 30,
                                       y_axis: str = 'plays',
                                       user_id: str = None,
                                       grouping: int = 0) -> Dict[str, Any]:
        """Get plays by top 10 platforms"""
        params = {'time_range': time_range, 'y_axis': y_axis, 'grouping': grouping}
        if user_id:
            params['user_id'] = user_id
        return self._make_request('get_plays_by_top_10_platforms', params)
    
    def get_user_player_stats(self, user_id: int, grouping: int = 0) -> Dict[str, Any]:
        """Get user's player statistics"""
        params = {'user_id': user_id, 'grouping': grouping}
        return self._make_request('get_user_player_stats', params)
    
    def get_metadata(self, rating_key: int) -> Dict[str, Any]:
        """Get metadata for a specific item"""
        params = {'rating_key': rating_key}
        return self._make_request('get_metadata', params)
    
    def get_libraries(self) -> Dict[str, Any]:
        """Get all libraries"""
        return self._make_request('get_libraries')
    
    def get_library_media_info(self, section_id: int, length: int = 10000) -> Dict[str, Any]:
        """Get media info for a library section"""
        params = {'section_id': section_id, 'length': length}
        return self._make_request('get_library_media_info', params)
    
    def get_users(self) -> Dict[str, Any]:
        """Get all users"""
        return self._make_request('get_users')
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get a specific user's details including profile picture"""
        params = {'user_id': user_id}
        return self._make_request('get_user', params)
    
    def plex_thumbnail_url(self, rating_key: int, image_name: str) -> str:
        """Generate Plex thumbnail URL"""
        return f'{self.plex_base_url}/library/metadata/{rating_key}/thumb/{image_name}?X-Plex-Token={self.plex_token}'
