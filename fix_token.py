"""
Fix: Use Page Access Token instead of User Access Token for Business Discovery.
Meta's Business Discovery API often requires a Page Token, not just a User Token.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
api_version = os.getenv("GRAPH_API_VERSION", "v19.0")

print("=" * 60)
print("  Fixing Token: Getting Page Access Token")
print("=" * 60)

# Step 1: Get Pages with their Page Access Tokens
print("\n[1/3] Fetching your Facebook Pages with Page Tokens...")
url = f"https://graph.facebook.com/{api_version}/me/accounts?fields=id,name,access_token,instagram_business_account&access_token={token}"
resp = requests.get(url, timeout=15)

if resp.status_code != 200:
    print(f"  ❌ Failed: {resp.json().get('error', {}).get('message', resp.text)}")
    exit(1)

pages = resp.json().get("data", [])
if not pages:
    print("  ❌ No Facebook Pages found!")
    exit(1)

# Find the page with linked IG account
page_token = None
ig_id = None
page_name = None

for page in pages:
    ig = page.get("instagram_business_account", {})
    if ig.get("id"):
        page_token = page.get("access_token")
        ig_id = ig["id"]
        page_name = page.get("name")
        break

if not page_token or not ig_id:
    print("  ❌ No Facebook Page with linked Instagram Business account found!")
    exit(1)

print(f"  ✅ Found Page: \"{page_name}\"")
print(f"  ✅ Instagram Business ID: {ig_id}")
print(f"  ✅ Page Token starts with: {page_token[:20]}...")

# Step 2: Test Business Discovery with Page Token
print("\n[2/3] Testing Business Discovery with PAGE Token...")
test_username = "jokowi"
fields = f"business_discovery.username({test_username}){{id,username,name,followers_count,media_count}}"
url = f"https://graph.facebook.com/{api_version}/{ig_id}?fields={fields}&access_token={page_token}"
resp = requests.get(url, timeout=15)

if resp.status_code == 200:
    bd = resp.json().get("business_discovery", {})
    print(f"  ✅ SUCCESS! Business Discovery WORKS with Page Token!")
    print(f"     Profile: {bd.get('name')} (@{bd.get('username')})")
    print(f"     Followers: {bd.get('followers_count')} | Posts: {bd.get('media_count')}")
    
    # Step 3: Update .env
    print(f"\n[3/3] Updating your .env file...")
    
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    # Read current .env
    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace token and business ID
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("INSTAGRAM_ACCESS_TOKEN="):
            new_lines.append(f"INSTAGRAM_ACCESS_TOKEN={page_token}")
        elif line.startswith("INSTAGRAM_BUSINESS_ACCOUNT_ID="):
            new_lines.append(f"INSTAGRAM_BUSINESS_ACCOUNT_ID={ig_id}")
        else:
            new_lines.append(line)
    
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
    
    print(f"  ✅ .env updated with Page Token & correct Business Account ID!")
    print()
    print("=" * 60)
    print("  🎉 FIXED! Now run your scraper:")
    print(f"  python main_scrape_instagram.py jokowi --max-posts 5")
    print("=" * 60)

else:
    err = resp.json().get("error", {})
    print(f"  ❌ Still failed with Page Token!")
    print(f"     Error: {err.get('message', resp.text)}")
    print(f"\n  Possible causes:")
    print(f"  1. Your app might need to be switched to 'Live' mode")
    print(f"     → Go to App Dashboard → toggle 'App Mode' from Development to Live")
    print(f"  2. Or Instagram Graph API product is not added to your app")
    print(f"     → Go to App Dashboard → Add Products → Instagram Graph API → Set Up")
