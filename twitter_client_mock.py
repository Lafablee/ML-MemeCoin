#twitter_client_mock.py
import logging
import json
import random
import string
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from config import Config

class TwitterClientMock:
    """
    Mock Twitter/X API client that simulates how media URLs are formatted
    in the Twitter API responses.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the mock Twitter client
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.twitter.com/2"
        
    def get_media_urls_format(self) -> Dict[str, Any]:
        """
        Returns sample media URLs in the format that Twitter API would return
        
        Returns:
            Dictionary with sample media URL formats
        """
        # Generate random media IDs for demonstration
        image_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        video_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        animated_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        user_id = '123456789'
        
        return {
            "formats": {
                "photo": f"https://pbs.twimg.com/media/{image_id}.jpg",
                "photo_large": f"https://pbs.twimg.com/media/{image_id}?format=jpg&name=large",
                "photo_medium": f"https://pbs.twimg.com/media/{image_id}?format=jpg&name=medium",
                "photo_small": f"https://pbs.twimg.com/media/{image_id}?format=jpg&name=small",
                "video": f"https://video.twimg.com/ext_tw_video/{video_id}/pu/vid/1280x720/{video_id}.mp4",
                "video_thumbnail": f"https://pbs.twimg.com/ext_tw_video_thumb/{video_id}/pu/img/thumbnail.jpg",
                "animated_gif": f"https://video.twimg.com/tweet_video/{animated_id}.mp4",
                "animated_gif_thumbnail": f"https://pbs.twimg.com/tweet_video_thumb/{animated_id}.jpg",
                "profile_image": f"https://pbs.twimg.com/profile_images/{user_id}/profile.jpg",
                "profile_banner": f"https://pbs.twimg.com/profile_banners/{user_id}/1234567890/1500x500"
            },
            "usage": (
                "These are the formats Twitter API uses for media URLs. "
                "When implementing the real API integration, you should use these formats "
                "to extract the direct media URLs from the API responses."
            )
        }
    
    def get_mock_tweet_with_media(self, tweet_id: str = None, username: str = None) -> Dict[str, Any]:
        """
        Generates a mock tweet with media in Twitter API v2 format
        
        Args:
            tweet_id: Optional tweet ID (random if not provided)
            username: Optional username (random if not provided)
            
        Returns:
            Mock tweet data with media in Twitter API format
        """
        # Generate random IDs if not provided
        if not tweet_id:
            tweet_id = ''.join(random.choices(string.digits, k=19))
        
        if not username:
            username = ''.join(random.choices(string.ascii_lowercase, k=8))
        
        # Generate random media IDs
        media_key_1 = ''.join(random.choices(string.digits, k=19))
        media_key_2 = ''.join(random.choices(string.digits, k=19))
        image_id_1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        image_id_2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
        
        # Generate mock tweet data
        tweet_time = (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat()
        
        # This structure matches Twitter API v2 response format
        tweet_data = {
            "data": {
                "id": tweet_id,
                "text": f"This is a sample tweet with media from @{username}! #sample #test",
                "created_at": tweet_time,
                "author_id": "12345678901234567890",
                "attachments": {
                    "media_keys": [
                        f"{media_key_1}",
                        f"{media_key_2}"
                    ]
                },
                "public_metrics": {
                    "retweet_count": random.randint(1, 1000),
                    "reply_count": random.randint(1, 100),
                    "like_count": random.randint(1, 5000),
                    "quote_count": random.randint(1, 50)
                }
            },
            "includes": {
                "users": [
                    {
                        "id": "12345678901234567890",
                        "name": f"{username.capitalize()} User",
                        "username": username,
                        "profile_image_url": f"https://pbs.twimg.com/profile_images/12345678901234567890/profile.jpg"
                    }
                ],
                "media": [
                    {
                        "media_key": f"{media_key_1}",
                        "type": "photo",
                        "url": f"https://pbs.twimg.com/media/{image_id_1}.jpg",
                        "width": 1200,
                        "height": 800
                    },
                    {
                        "media_key": f"{media_key_2}",
                        "type": "photo",
                        "url": f"https://pbs.twimg.com/media/{image_id_2}.jpg",
                        "width": 1200,
                        "height": 800
                    }
                ]
            }
        }
        
        return tweet_data
    
    def get_tweet_media_urls(self, tweet_id: str) -> List[str]:
        """
        Simulates getting media URLs from a tweet
        
        Args:
            tweet_id: Tweet ID
            
        Returns:
            List of media URLs
        """
        # In a real implementation, this would call the Twitter API
        # For now, we generate mock data
        mock_tweet = self.get_mock_tweet_with_media(tweet_id=tweet_id)
        
        # Extract media URLs
        media_urls = []
        if "includes" in mock_tweet and "media" in mock_tweet["includes"]:
            for media in mock_tweet["includes"]["media"]:
                if "url" in media:
                    media_urls.append(media["url"])
        
        return media_urls

# Example usage
if __name__ == "__main__":
    from config import Config
    
    config = Config()
    client = TwitterClientMock(config)
    
    # Show sample media URL formats
    formats = client.get_media_urls_format()
    print("\nTwitter API Media URL Formats:")
    for media_type, url_format in formats["formats"].items():
        print(f"{media_type}: {url_format}")
    
    print("\n" + formats["usage"])
    
    # Generate a mock tweet with media
    mock_tweet = client.get_mock_tweet_with_media(username="testuser")
    print("\nMock Tweet with Media (Twitter API v2 format):")
    print(json.dumps(mock_tweet, indent=2))
    
    # Get media URLs from a tweet
    media_urls = client.get_tweet_media_urls("123456789")
    print("\nExtracted Media URLs:")
    for url in media_urls:
        print(url)