import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseInstagramScraper

class InstagramGraphAPIScraper(BaseInstagramScraper):
    """
    Official Meta Instagram Graph API Scraper using Business Discovery API.
    
    Documentation:
    https://developers.facebook.com/docs/instagram-api/guides/business-discovery
    
    Requirements:
    - Meta Access Token (User or Page Access Token)
    - Instagram Business / Creator Account ID linked to a Facebook Page
    """

    BASE_URL = "https://graph.facebook.com"

    def __init__(self, access_token: Optional[str] = None, business_account_id: Optional[str] = None, api_version: str = "v19.0"):
        self.access_token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.business_account_id = business_account_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        self.api_version = api_version or os.getenv("GRAPH_API_VERSION", "v19.0")

        if not self.access_token:
            raise ValueError("INSTAGRAM_ACCESS_TOKEN is required for Meta Graph API scraper.")
        if not self.business_account_id:
            raise ValueError("INSTAGRAM_BUSINESS_ACCOUNT_ID is required for Meta Graph API Business Discovery.")

    def scrape_profile(self, username: str, max_posts: int = 15, max_comments_per_post: int = 20) -> Dict[str, Any]:
        """
        Fetch public profile and media details using Instagram Business Discovery API.
        """
        clean_username = username.lstrip("@").strip()
        endpoint = f"{self.BASE_URL}/{self.api_version}/{self.business_account_id}"

        fields = (
            f"business_discovery.username({clean_username}){{"
            f"id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url,"
            f"media.limit({max_posts}){{"
            f"id,caption,comments_count,like_count,media_type,media_url,permalink,timestamp,"
            f"comments.limit({max_comments_per_post}){{"
            f"id,text,username,timestamp"
            f"}}"
            f"}}"
            f"}}"
        )

        params = {
            "fields": fields,
            "access_token": self.access_token
        }

        response = requests.get(endpoint, params=params, timeout=30)
        
        if response.status_code != 200:
            error_data = response.json().get("error", {})
            error_msg = error_data.get("message", response.text)
            error_code = error_data.get("code", "Unknown")
            raise Exception(f"Meta Graph API Error ({error_code}): {error_msg}")

        data = response.json()

        if "business_discovery" not in data:
            raise Exception(f"No business_discovery data returned for username: {clean_username}")

        discovery = data["business_discovery"]
        
        # Parse profile details
        profile = {
            "username": discovery.get("username", clean_username),
            "full_name": discovery.get("name", ""),
            "biography": discovery.get("biography", ""),
            "followers_count": discovery.get("followers_count", 0),
            "following_count": discovery.get("follows_count", 0),
            "media_count": discovery.get("media_count", 0),
            "profile_picture_url": discovery.get("profile_picture_url", ""),
            "is_verified": False, # Graph API business discovery does not return verified badge directly
            "is_business": True   # Business discovery targets business/creator accounts
        }

        # Parse posts
        posts = []
        media_list = discovery.get("media", {}).get("data", [])

        for media in media_list:
            # Parse comments
            comments = []
            comments_data = media.get("comments", {}).get("data", [])
            for c in comments_data:
                comments.append({
                    "comment_id": c.get("id"),
                    "text": c.get("text", ""),
                    "username": c.get("username", "anonymous"),
                    "timestamp": c.get("timestamp", ""),
                    "like_count": None
                })

            posts.append({
                "post_id": media.get("id"),
                "caption": media.get("caption", ""),
                "timestamp": media.get("timestamp", ""),
                "like_count": media.get("like_count", 0),
                "comments_count": media.get("comments_count", 0),
                "media_type": media.get("media_type", "UNKNOWN"),
                "permalink": media.get("permalink", ""),
                "media_url": media.get("media_url", ""),
                "comments": comments
            })

        return {
            "platform": "instagram",
            "scraper_type": "meta_graph_api",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "profile": profile,
            "posts": posts
        }
