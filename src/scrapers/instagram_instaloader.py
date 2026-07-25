import os
import re
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
        session_id = os.getenv("INSTAGRAM_SESSION_ID")

        # Method 1: Browser session cookie (most reliable, bypasses bot detection)
        if session_id and session_id != "your_sessionid_cookie_value_here":
            try:
                self._login_with_session_id(session_id, ig_user)
                print(f"[Instaloader] Logged in via browser session cookie.")
                return
            except Exception as e:
                print(f"[Instaloader] Session cookie login failed: {e}. Trying other methods...")

        # Method 2: Load saved session file
        if ig_user:
            try:
                self.loader.load_session_from_file(ig_user)
                print(f"[Instaloader] Session loaded from file for @{ig_user}")
                return
            except FileNotFoundError:
                print(f"[Instaloader] No session file found for @{ig_user}. Trying password login...")
            except Exception as e:
                print(f"[Instaloader] Session file error: {e}. Trying password login...")

            # Method 3: Password login (least reliable)
            if ig_pass:
                try:
                    self.loader.login(ig_user, ig_pass)
                    self.loader.save_session_to_file()
                    print(f"[Instaloader] Logged in as @{ig_user} and session saved.")
                except Exception as e:
                    print(f"[Warning] Instaloader login failed: {e}. Proceeding anonymously...")

    def _login_with_session_id(self, session_id: str, username: Optional[str] = None):
        """
        Login to Instagram using the sessionid cookie obtained from a browser.
        This is the most reliable method as it reuses an existing browser session.
        """
        import requests
        # Get username from session if not provided
        if not username:
            resp = requests.get(
                "https://www.instagram.com/api/v1/accounts/current_user/?edit=true",
                headers={"User-Agent": "Mozilla/5.0"},
                cookies={"sessionid": session_id},
                timeout=15
            )
            if resp.status_code == 200:
                username = resp.json().get("user", {}).get("username", "user")
            else:
                username = "user"

        self.loader.context._session.cookies.update({
            "sessionid": session_id,
            "ds_user_id": "",
        })
        self.loader.context.username = username

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
