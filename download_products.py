import requests
from bs4 import BeautifulSoup
import os
import re
import json

BASE_URL = "https://menu.myqrcodemenu.com"
MENU_SLUG = "the-churroll-caddebostan-193bcd"
SAVE_DIR = r"C:\Users\ByMED\Desktop\Qr Churroll\site"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
}

CATEGORIES = [
    ("Churros",         "a9064814-8e51-44a9-8048-fd97291d83d1"),
    ("Sıcak İçecekler", "65ff6611-aab2-4234-a662-53a5f25accb0"),
    ("Soğuk İçecekler", "4dd5330a-5020-4275-bf91-efefa2147af4"),
    ("Ekstralar",       "aa7462f5-1ad8-4a95-a1cf-efea8721b65c"),
]

def save_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            print(f"  [OK] {os.path.basename(save_path)[:70]}")
            return True
        else:
            print(f"  [SKIP {r.status_code}] {url}")
            return False
    except Exception as e:
        print(f"  [ERR] {e}")
        return False

all_images = set()

for cat_name, cat_id in CATEGORIES:
    url = f"{BASE_URL}/menu/{MENU_SLUG}/tr/categories/{cat_id}"
    print(f"\nKategori: {cat_name}")
    r = requests.get(url, headers=HEADERS, timeout=30)
    html = r.text

    # ProductPicture from JSON data embedded in ng-click attributes
    # Pattern: "ProductPicture":"filename.jpg"
    pics = re.findall(r'"ProductPicture"\s*:\s*"([^"]+)"', html)
    for p in pics:
        if p and not p.startswith("{{"):
            all_images.add(p)
            print(f"  + {p}")

    # Also img src
    soup = BeautifulSoup(html, "lxml")
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if "/files/products/" in src and "{{" not in src:
            fname = src.split("/files/products/")[-1]
            all_images.add(fname)
            print(f"  + {fname[:60]}")

print(f"\n\nToplam {len(all_images)} ürün resmi bulundu")
print("\nResimler indiriliyor...")

for img in all_images:
    if img.startswith("http"):
        url = img
    else:
        url = f"{BASE_URL}/files/products/{img}"
    
    local_path = os.path.join(SAVE_DIR, "files", "products", img)
    save_file(url, local_path)

# Özet
total_files = sum(len(files) for _, _, files in os.walk(SAVE_DIR))
total_size = sum(
    os.path.getsize(os.path.join(rr, f))
    for rr, _, files in os.walk(SAVE_DIR) for f in files
)
print(f"\nToplam: {total_files} dosya | {total_size/1024/1024:.1f} MB")
print(f"Klasör: {SAVE_DIR}")
