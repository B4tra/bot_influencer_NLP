"""
Check what permissions are currently attached to your Access Token.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
api_version = os.getenv("GRAPH_API_VERSION", "v19.0")

print("=" * 60)
print("  Checking Token Permissions")
print("=" * 60)

# Check current permissions
url = f"https://graph.facebook.com/{api_version}/me/permissions?access_token={token}"
resp = requests.get(url, timeout=15)

if resp.status_code == 200:
    permissions = resp.json().get("data", [])
    
    required = ["instagram_basic", "pages_read_engagement", "pages_show_list", "business_management"]
    
    print("\nIzin yang SUDAH ada di token Anda:")
    print("-" * 40)
    for p in permissions:
        name = p.get("permission")
        status = p.get("status")
        icon = "✅" if status == "granted" else "❌"
        print(f"  {icon} {name} → {status}")
    
    granted_names = [p["permission"] for p in permissions if p["status"] == "granted"]
    
    print("\nIzin yang DIBUTUHKAN tapi BELUM ada:")
    print("-" * 40)
    missing = [r for r in required if r not in granted_names]
    if missing:
        for m in missing:
            print(f"  ❌ {m} → MISSING!")
        print(f"\n⚠️  Anda perlu menambahkan izin di atas di Graph API Explorer,")
        print(f"   lalu Generate Access Token ulang.")
    else:
        print("  ✅ Semua izin yang dibutuhkan sudah ada!")
        print("  → Jika masih error, coba generate token baru dan pastikan")
        print("    mencentang Facebook Page di popup konfirmasi.")
else:
    err = resp.json().get("error", {})
    print(f"❌ Gagal mengecek izin: {err.get('message', resp.text)}")
