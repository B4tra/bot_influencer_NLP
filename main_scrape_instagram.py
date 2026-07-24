import sys
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

from src.scrapers import get_instagram_scraper
from src.utils import DataExporter

def main():
    parser = argparse.ArgumentParser(description="Instagram Scraper - Official Meta Graph API & Fallback Scraper")
    parser.add_argument("username", nargs="?", help="Target Instagram username (e.g. instagram or @instagram)")
    parser.add_argument("--mode", choices=["auto", "graph_api", "instaloader"], default="auto", help="Scraper mode (default: auto)")
    parser.add_argument("--max-posts", type=int, default=10, help="Maximum posts to fetch (default: 10)")
    parser.add_argument("--max-comments", type=int, default=15, help="Maximum comments per post (default: 15)")
    parser.add_argument("--output-dir", default="data/raw", help="Directory to save output files (default: data/raw)")

    args = parser.parse_args()

    if not args.username:
        print("Usage example:")
        print("  python main_scrape_instagram.py instagram")
        print("  python main_scrape_instagram.py @username --mode graph_api --max-posts 20")
        sys.exit(1)

    clean_username = args.username.lstrip("@")
    print(f"=== Scraping Instagram Profile: @{clean_username} ===")
    print(f"Mode: {args.mode}")
    print(f"Max Posts: {args.max_posts} | Max Comments/Post: {args.max_comments}")

    force_mode = None if args.mode == "auto" else args.mode

    try:
        scraper = get_instagram_scraper(prefer_official=True, force_mode=force_mode)
        data = scraper.scrape_profile(
            username=clean_username,
            max_posts=args.max_posts,
            max_comments_per_post=args.max_comments
        )

        exporter = DataExporter(output_dir=args.output_dir)
        json_path, p_csv, post_csv, c_csv = exporter.save_all(data)

        print("\n[Success] Data scraping completed!")
        print(f"Scraper Used: {data.get('scraper_type')}")
        print(f"Profile: {data['profile']['full_name']} (@{data['profile']['username']})")
        print(f"Followers: {data['profile']['followers_count']} | Posts fetched: {len(data['posts'])}")
        print("\nSaved files:")
        print(f"  - Raw JSON : {json_path}")
        print(f"  - Profile CSV  : {p_csv}")
        print(f"  - Posts CSV    : {post_csv}")
        print(f"  - Comments CSV : {c_csv}")

    except Exception as e:
        print(f"\n[Error] Scraping failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
