import requests
import re
import os
import json

BASE_URL = "https://menu.myqrcodemenu.com"
MENU_SLUG = "the-churroll-caddebostan-193bcd"
SAVE_DIR = r"C:\Users\ByMED\Desktop\Qr Churroll\site"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9",
    "Referer": f"{BASE_URL}/menu/{MENU_SLUG}/tr"
}

def save_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            print(f"  [OK] .../{os.path.basename(save_path)[:70]}")
            return True
        else:
            print(f"  [SKIP {r.status_code}] {url}")
            return False
    except Exception as e:
        print(f"  [ERR] {url}: {e}")
        return False

# Read master.js to find API endpoint patterns
print("[*] master.js analiz ediliyor...")
js_dir = os.path.join(SAVE_DIR, "js")
js_file = None
if os.path.exists(js_dir):
    for f in os.listdir(js_dir):
        if "master" in f:
            js_file = os.path.join(js_dir, f)
            break

api_patterns = []
if js_file:
    with open(js_file, "r", encoding="utf-8", errors="ignore") as f:
        js = f.read()
    # Find API URLs
    api_matches = re.findall(r'["\']/?api/[^"\']+["\']', js)
    for m in api_matches[:20]:
        print(" ", m.strip("'\""))
        api_patterns.append(m.strip("'\""))

# Try common API endpoints
print("\n[*] API endpoint'leri deneniyor...")
api_endpoints = [
    f"/api/menu/{MENU_SLUG}",
    f"/api/menus/{MENU_SLUG}",
    f"/api/v1/menu/{MENU_SLUG}",
    f"/api/v1/menus/{MENU_SLUG}",
    f"/menupublic/getmenu?slug={MENU_SLUG}",
    f"/api/public/menu/{MENU_SLUG}",
]

menu_data = None
for ep in api_endpoints:
    try:
        r = requests.get(BASE_URL + ep, headers=HEADERS, timeout=15)
        print(f"  {ep} -> {r.status_code}")
        if r.status_code == 200:
            try:
                menu_data = r.json()
                print(f"    ✓ JSON data alındı! Keys: {list(menu_data.keys()) if isinstance(menu_data, dict) else type(menu_data).__name__}")
                # Save
                with open(os.path.join(SAVE_DIR, "menu_data.json"), "w", encoding="utf-8") as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=2)
                break
            except:
                pass
    except Exception as e:
        print(f"  {ep} -> ERR: {e}")

# If we found menu data, extract all product images
if menu_data:
    print("\n[*] Ürün resimleri çıkarılıyor...")
    def extract_images(obj, depth=0):
        images = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in ('picture', 'image', 'photo', 'img', 'logo', 'icon', 'thumbnail') and isinstance(v, str) and v:
                    images.append(v)
                else:
                    images.extend(extract_images(v, depth+1))
        elif isinstance(obj, list):
            for item in obj:
                images.extend(extract_images(item, depth+1))
        elif isinstance(obj, str):
            if re.search(r'\.(jpg|jpeg|png|gif|webp)$', obj, re.I):
                images.append(obj)
        return images
    
    all_images = list(set(extract_images(menu_data)))
    print(f"  {len(all_images)} resim bulundu")
    
    for img in all_images:
        if img.startswith("/files/") or img.startswith("files/"):
            url = BASE_URL + ("/" + img.lstrip("/"))
        elif img.startswith("http"):
            url = img
        else:
            url = BASE_URL + "/files/products/" + img
        
        path_part = urlparse(url).path if url.startswith("http") else url
        save_path = os.path.join(SAVE_DIR, path_part.lstrip("/").replace("/", os.sep))
        save_file(url, save_path)

print("\n[*] Bitti!")
total_files = sum(len(files) for _, _, files in os.walk(SAVE_DIR))
total_size = sum(
    os.path.getsize(os.path.join(r, f))
    for r, _, files in os.walk(SAVE_DIR) for f in files
)
print(f"Toplam: {total_files} dosya, {total_size / 1024 / 1024:.1f} MB")
