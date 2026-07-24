import os
from typing import Optional
from .base import BaseInstagramScraper
from .instagram_graph_api import InstagramGraphAPIScraper
from .instagram_instaloader import InstaloaderScraper

def get_instagram_scraper(prefer_official: bool = True, force_mode: Optional[str] = None) -> BaseInstagramScraper:
    """
    Factory function to get appropriate Instagram Scraper.
    
    Args:
        prefer_official: If True (default), uses Meta Graph API if access token & account ID are available in env.
        force_mode: Force specific scraper mode: 'graph_api' or 'instaloader'
        
    Returns:
        Instance of BaseInstagramScraper subclass.
    """
    if force_mode == "graph_api":
        return InstagramGraphAPIScraper()
    elif force_mode == "instaloader":
        return InstaloaderScraper()

    token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    business_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")

    if prefer_official and token and business_id:
        print("[Factory] Meta Graph API credentials found. Using InstagramGraphAPIScraper (Official API).")
        try:
            return InstagramGraphAPIScraper()
        except Exception as e:
            print(f"[Factory] Failed to initialize Meta Graph API: {e}. Falling back to Instaloader...")
            return InstaloaderScraper()
    else:
        print("[Factory] Using InstaloaderScraper (Fallback mode).")
        return InstaloaderScraper()
