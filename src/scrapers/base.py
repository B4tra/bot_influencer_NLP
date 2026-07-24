from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseInstagramScraper(ABC):
    """
    Abstract Base Class for Instagram Scrapers.
    Ensures both Meta Graph API and fallback scrapers return standardized data.
    """

    @abstractmethod
    def scrape_profile(self, username: str, max_posts: int = 15, max_comments_per_post: int = 20) -> Dict[str, Any]:
        """
        Scrape profile details, posts, and comments for a given Instagram username.

        Args:
            username: Target Instagram username (without @)
            max_posts: Maximum number of recent posts to retrieve
            max_comments_per_post: Maximum number of comments to retrieve per post

        Returns:
            Dict structured as:
            {
                "platform": "instagram",
                "scraper_type": str,
                "scraped_at": str (ISO 8601),
                "profile": {
                    "username": str,
                    "full_name": str,
                    "biography": str,
                    "followers_count": int,
                    "following_count": int,
                    "media_count": int,
                    "profile_picture_url": str,
                    "is_verified": bool,
                    "is_business": bool,
                },
                "posts": [
                    {
                        "post_id": str,
                        "caption": str,
                        "timestamp": str,
                        "like_count": int,
                        "comments_count": int,
                        "media_type": str, # IMAGE, VIDEO, CAROUSEL_ALBUM
                        "permalink": str,
                        "media_url": str,
                        "comments": [
                            {
                                "comment_id": str,
                                "text": str,
                                "username": str,
                                "timestamp": str,
                                "like_count": Optional[int]
                            }
                        ]
                    }
                ]
            }
        """
        pass
