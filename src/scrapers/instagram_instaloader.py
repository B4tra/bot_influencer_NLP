import os
import instaloader
from datetime import datetime
from typing import Dict, Any, Optional
from .base import BaseInstagramScraper

class InstaloaderScraper(BaseInstagramScraper):
    """
    Fallback Instagram scraper using Instaloader library.
    Used when Meta Graph API tokens are unavailable or for personal accounts.
    """

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_comments=True,
            save_metadata=False,
            compress_json=False
        )

        ig_user = username or os.getenv("INSTAGRAM_USERNAME")
        ig_pass = password or os.getenv("INSTAGRAM_PASSWORD")

        if ig_user and ig_pass:
            try:
                self.loader.login(ig_user, ig_pass)
            except Exception as e:
                print(f"[Warning] Instaloader login failed: {e}. Proceeding anonymously...")

    def scrape_profile(self, username: str, max_posts: int = 15, max_comments_per_post: int = 20) -> Dict[str, Any]:
        """
        Scrape Instagram profile data and recent posts using Instaloader.
        """
        clean_username = username.lstrip("@").strip()
        
        try:
            profile_data = instaloader.Profile.from_username(self.loader.context, clean_username)
        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Instagram profile '@{clean_username}' not found.")
        except Exception as e:
            raise Exception(f"Instaloader error fetching profile '@{clean_username}': {e}")

        profile = {
            "username": profile_data.username,
            "full_name": profile_data.full_name or "",
            "biography": profile_data.biography or "",
            "followers_count": profile_data.followers,
            "following_count": profile_data.followees,
            "media_count": profile_data.mediacount,
            "profile_picture_url": profile_data.profile_pic_url or "",
            "is_verified": profile_data.is_verified,
            "is_business": profile_data.is_business_account
        }

        posts = []
        posts_iterator = profile_data.get_posts()

        for idx, post in enumerate(posts_iterator):
            if idx >= max_posts:
                break

            comments = []
            if max_comments_per_post > 0:
                try:
                    comment_idx = 0
                    for comment in post.get_comments():
                        if comment_idx >= max_comments_per_post:
                            break
                        comments.append({
                            "comment_id": str(comment.id),
                            "text": comment.text or "",
                            "username": comment.owner.username if comment.owner else "anonymous",
                            "timestamp": comment.created_at_utc.isoformat() + "Z" if comment.created_at_utc else "",
                            "like_count": comment.likes_count if hasattr(comment, 'likes_count') else None
                        })
                        comment_idx += 1
                except Exception as e:
                    # Non-fatal comment fetch error (e.g. rate limit on comments)
                    pass

            media_type = "IMAGE"
            if post.is_video:
                media_type = "VIDEO"
            elif post.typename == "GraphSidecar":
                media_type = "CAROUSEL_ALBUM"

            posts.append({
                "post_id": post.shortcode or str(post.mediaid),
                "caption": post.caption or "",
                "timestamp": post.date_utc.isoformat() + "Z" if post.date_utc else "",
                "like_count": post.likes,
                "comments_count": post.comments,
                "media_type": media_type,
                "permalink": f"https://www.instagram.com/p/{post.shortcode}/" if post.shortcode else "",
                "media_url": post.url or "",
                "comments": comments
            })

        return {
            "platform": "instagram",
            "scraper_type": "instaloader",
            "scraped_at": datetime.utcnow().isoformat() + "Z",
            "profile": profile,
            "posts": posts
        }
