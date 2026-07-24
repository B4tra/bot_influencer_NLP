"""
Diagnostic script to verify Meta Graph API credentials and permissions.
Run this BEFORE using the main scraper to ensure your .env is correctly configured.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  Instagram Graph API - Diagnostic Tool")
print("=" * 60)

# Step 1: Check .env values exist
token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
business_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
api_version = os.getenv("GRAPH_API_VERSION", "v19.0")

print("\n[1/4] Checking .env variables...")
if not token or token == "your_facebook_user_or_page_access_token_here":
    print("  ❌ INSTAGRAM_ACCESS_TOKEN is missing or still set to placeholder!")
    print("     → Generate a token at: https://developers.facebook.com/tools/explorer/")
    exit(1)
else:
    print(f"  ✅ INSTAGRAM_ACCESS_TOKEN found (starts with: {token[:15]}...)")

if not business_id or business_id == "your_instagram_business_account_id_here":
    print("  ⚠️  INSTAGRAM_BUSINESS_ACCOUNT_ID is missing or still set to placeholder.")
    print("     → We will try to find it automatically in Step 3.")
else:
    print(f"  ✅ INSTAGRAM_BUSINESS_ACCOUNT_ID found: {business_id}")

print(f"  ✅ GRAPH_API_VERSION: {api_version}")

# Step 2: Test token validity
print("\n[2/4] Testing Access Token validity...")
url = f"https://graph.facebook.com/{api_version}/me?fields=id,name&access_token={token}"
resp = requests.get(url, timeout=15)
if resp.status_code == 200:
    data = resp.json()
    print(f"  ✅ Token is VALID! Logged in as: {data.get('name')} (ID: {data.get('id')})")
else:
    err = resp.json().get("error", {})
    print(f"  ❌ Token is INVALID or EXPIRED!")
    print(f"     Error: {err.get('message', resp.text)}")
    print(f"     → Please generate a new token at Graph API Explorer.")
    exit(1)

# Step 3: Check Facebook Pages & linked Instagram accounts
print("\n[3/4] Finding Facebook Pages & linked Instagram Business accounts...")
url = f"https://graph.facebook.com/{api_version}/me/accounts?fields=id,name,instagram_business_account&access_token={token}"
resp = requests.get(url, timeout=15)
if resp.status_code == 200:
    pages = resp.json().get("data", [])
    if not pages:
        print("  ❌ No Facebook Pages found linked to this token!")
        print("     → When generating the token, you MUST check/select your Facebook Page")
        print("       in the confirmation popup window.")
        print("     → Also make sure your Instagram account is connected to a Facebook Page.")
        exit(1)
    
    found_ig = False
    for page in pages:
        ig_account = page.get("instagram_business_account", {})
        ig_id = ig_account.get("id", "NOT LINKED")
        status = "✅" if ig_account else "⚠️ No IG linked"
        print(f"  {status} Page: \"{page.get('name')}\" (ID: {page.get('id')}) → IG Business ID: {ig_id}")
        if ig_account:
            found_ig = True
            correct_id = ig_id
    
    if not found_ig:
        print("\n  ❌ None of your Facebook Pages have a linked Instagram Business account!")
        print("     → Open Instagram app → Settings → Account → Switch to Business/Creator account")
        print("     → Then link it to your Facebook Page.")
        exit(1)
    else:
        if not business_id or business_id == "your_instagram_business_account_id_here":
            print(f"\n  💡 Auto-detected! Set this in your .env file:")
            print(f"     INSTAGRAM_BUSINESS_ACCOUNT_ID={correct_id}")
else:
    err = resp.json().get("error", {})
    print(f"  ❌ Failed to fetch Pages!")
    print(f"     Error: {err.get('message', resp.text)}")
    print(f"     → This usually means the token is missing 'pages_show_list' or")
    print(f"       'pages_read_engagement' permissions.")
    print(f"     → Re-generate your token with all required permissions.")
    exit(1)

# Step 4: Test Business Discovery (the actual scraping call)
print("\n[4/4] Testing Business Discovery API (scraping @jokowi as test)...")
test_username = "jokowi"
if business_id and business_id != "your_instagram_business_account_id_here":
    target_id = business_id
else:
    target_id = correct_id

fields = f"business_discovery.username({test_username}){{id,username,name,followers_count,media_count}}"
url = f"https://graph.facebook.com/{api_version}/{target_id}?fields={fields}&access_token={token}"
resp = requests.get(url, timeout=15)

if resp.status_code == 200:
    bd = resp.json().get("business_discovery", {})
    print(f"  ✅ Business Discovery WORKS!")
    print(f"     Profile: {bd.get('name')} (@{bd.get('username')})")
    print(f"     Followers: {bd.get('followers_count')} | Posts: {bd.get('media_count')}")
    print("\n" + "=" * 60)
    print("  🎉 ALL CHECKS PASSED! Your scraper is ready to use.")
    print("=" * 60)
else:
    err = resp.json().get("error", {})
    print(f"  ❌ Business Discovery FAILED!")
    print(f"     Error Code: {err.get('code')}")
    print(f"     Message: {err.get('message', resp.text)}")
    if err.get("code") == 10:
        print(f"\n     → Error #10 means your token is missing 'instagram_basic' permission.")
        print(f"     → Go to Graph API Explorer, add 'instagram_basic' permission,")
        print(f"       then click 'Generate Access Token' again.")
        print(f"     → IMPORTANT: In the popup, make sure you CHECK your Facebook Page!")
    print()
