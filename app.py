import os
import logging
from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

def extract_video_id(url):
    """Extract YouTube video ID from URL."""
    # Handle different YouTube URL formats
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if parsed_url.hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def validate_youtube_url(url):
    """Validate if the URL is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return bool(re.match(youtube_regex, url))

@app.route('/')
def index():
    """Render the documentation page."""
    return render_template('index.html')

@app.route('/api/extract', methods=['POST'])
def extract_transcripts():
    """Extract transcripts from YouTube videos."""
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'urls' not in data:
            return jsonify({
                'error': 'Invalid request format. Expected {"urls": [...]}',
                'status': 'error'
            }), 400

        urls = data['urls']
        if not isinstance(urls, list):
            return jsonify({
                'error': 'URLs must be provided as a list',
                'status': 'error'
            }), 400

        results = []
        for url in urls:
            result = {
                'url': url,
                'status': 'pending',
                'transcript': None,
                'error': None
            }

            if not validate_youtube_url(url):
                result['status'] = 'error'
                result['error'] = 'Invalid YouTube URL'
                results.append(result)
                continue

            video_id = extract_video_id(url)
            if not video_id:
                result['status'] = 'error'
                result['error'] = 'Could not extract video ID'
                results.append(result)
                continue

            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                print(transcript)
                full_transcript = ""
                for entry in transcript:
                    start_time = entry["start"]
                    duration = entry["duration"]
                    end_time = start_time + duration
                    text = entry["text"].replace("\n", " ")
                    full_transcript += "\n" + str(start_time) + " - " + str(end_time) + ": " + text
                result['status'] = 'success'
                result['transcript'] = full_transcript
            except TranscriptsDisabled:
                result['status'] = 'error'
                result['error'] = 'Transcripts are disabled for this video'
            except NoTranscriptFound:
                result['status'] = 'error'
                result['error'] = 'No transcript found for this video'
            except Exception as e:
                logger.error(f"Error processing video {url}: {str(e)}")
                result['status'] = 'error'
                result['error'] = 'An unexpected error occurred'

            results.append(result)

        return jsonify({
            'results': results,
            'status': 'success'
        })

    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)