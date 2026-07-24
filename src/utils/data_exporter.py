import os
import json
import pandas as pd
from typing import Dict, Any, Tuple

class DataExporter:
    """
    Utility class to export scraped raw data into structured JSON and CSV files.
    """

    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_all(self, scraped_data: Dict[str, Any], filename_prefix: str = "") -> Tuple[str, str, str, str]:
        """
        Saves raw data into:
        1. Full JSON file (raw dict)
        2. Profile CSV
        3. Posts CSV
        4. Comments CSV

        Returns:
            Tuple of generated filepaths: (json_path, profile_csv, posts_csv, comments_csv)
        """
        username = scraped_data.get("profile", {}).get("username", "unknown")
        prefix = f"{filename_prefix}_{username}" if filename_prefix else username

        # 1. Full JSON
        json_path = os.path.join(self.output_dir, f"{prefix}_full.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=2)

        # 2. Profile CSV
        profile_data = scraped_data.get("profile", {})
        profile_df = pd.DataFrame([profile_data])
        profile_csv_path = os.path.join(self.output_dir, f"{prefix}_profile.csv")
        profile_df.to_csv(profile_csv_path, index=False, encoding="utf-8")

        # 3. Posts CSV
        posts_list = scraped_data.get("posts", [])
        flattened_posts = []
        flattened_comments = []

        for p in posts_list:
            post_flat = {k: v for k, v in p.items() if k != "comments"}
            post_flat["username"] = username
            flattened_posts.append(post_flat)

            for c in p.get("comments", []):
                comment_flat = {k: v for k, v in c.items()}
                comment_flat["post_id"] = p.get("post_id")
                comment_flat["target_username"] = username
                flattened_comments.append(comment_flat)

        posts_df = pd.DataFrame(flattened_posts)
        posts_csv_path = os.path.join(self.output_dir, f"{prefix}_posts.csv")
        posts_df.to_csv(posts_csv_path, index=False, encoding="utf-8")

        # 4. Comments CSV
        comments_df = pd.DataFrame(flattened_comments)
        comments_csv_path = os.path.join(self.output_dir, f"{prefix}_comments.csv")
        comments_df.to_csv(comments_csv_path, index=False, encoding="utf-8")

        return json_path, profile_csv_path, posts_csv_path, comments_csv_path
