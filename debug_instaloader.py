"""
Quick test to debug why Instaloader can't find profiles.
"""
import instaloader
import os
from dotenv import load_dotenv

load_dotenv()

ig_user = os.getenv("INSTAGRAM_USERNAME")

print("=" * 50)
print(f"Instaloader version: {instaloader.__version__}")
print(f"Testing with session: @{ig_user}")
print("=" * 50)

L = instaloader.Instaloader()

# Load session
try:
    L.load_session_from_file(ig_user)
    print(f"✅ Session loaded for @{ig_user}")
except Exception as e:
    print(f"❌ Session error: {e}")

# Test with a simple known account
test_accounts = ["jokowi", "instagram", "natgeo"]
for username in test_accounts:
    print(f"\nTesting @{username}...")
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        print(f"  ✅ Found! Followers: {profile.followers:,}")
        break
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"  ❌ ProfileNotExistsException")
    except instaloader.exceptions.QueryReturnedNotFoundException:
        print(f"  ❌ QueryReturnedNotFoundException (404 from Instagram - likely blocked)")
    except instaloader.exceptions.ConnectionException as e:
        print(f"  ❌ ConnectionException: {e}")
    except Exception as e:
        print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")
