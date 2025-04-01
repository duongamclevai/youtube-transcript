from typing import Dict, List, Optional
import re
from urllib.parse import urlparse, parse_qs

def create_response(status: str, results: Optional[List] = None, error: Optional[str] = None) -> Dict:
    """Create a standardized API response."""
    response = {
        'status': status
    }
    if results is not None:
        response['results'] = results
    if error is not None:
        response['error'] = error
    return response

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    patterns = [
        r'^https?:\/\/(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'^https?:\/\/(?:www\.)?youtube\.com\/embed\/([^?]+)',
        r'^https?:\/\/(?:www\.)?youtu\.be\/([^?]+)'
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    return None

def validate_request_data(data: Dict) -> tuple[bool, Optional[str]]:
    """Validate the incoming request data."""
    if not isinstance(data, dict):
        return False, "Request body must be a JSON object"
    
    if 'urls' not in data:
        return False, "Request must contain 'urls' field"
        
    if not isinstance(data['urls'], list):
        return False, "URLs must be provided as a list"
        
    if not all(isinstance(url, str) for url in data['urls']):
        return False, "All URLs must be strings"
        
    return True, None
