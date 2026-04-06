import requests
from bs4 import BeautifulSoup
import os
import re
import json
from urllib.parse import urljoin, urlparse
import time

BASE_URL = "https://menu.myqrcodemenu.com"
MENU_SLUG = "the-churroll-caddebostan-193bcd"
MENU_URL = f"{BASE_URL}/menu/{MENU_SLUG}/tr"
SAVE_DIR = r"C:\Users\ByMED\Desktop\Qr Churroll\site"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8"
}

CATEGORIES = [
    ("Churros", "a9064814-8e51-44a9-8048-fd97291d83d1"),
    ("Sıcak İçecekler", "65ff6611-aab2-4234-a662-53a5f25accb0"),
    ("Soğuk İçecekler", "4dd5330a-5020-4275-bf91-efefa2147af4"),
    ("Ekstralar", "aa7462f5-1ad8-4a95-a1cf-efea8721b65c"),
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
            print(f"  [OK] {url.split('/')[-1][:60]}")
            return True
        else:
            print(f"  [SKIP {r.status_code}] {url}")
            return False
    except Exception as e:
        print(f"  [ERR] {url}: {e}")
        return False

def url_to_path(url, base_dir):
    parsed = urlparse(url)
    path = parsed.path.lstrip('/')
    return os.path.join(base_dir, path.replace('/', os.sep))

def download_page_assets(html, page_url, base_dir):
    soup = BeautifulSoup(html, "lxml")
    assets = []
    
    # Scripts
    for tag in soup.find_all("script", src=True):
        src = tag["src"]
        if src.startswith("//"):
            src = "https:" + src
        if not src.startswith("http"):
            src = urljoin(BASE_URL, src)
        if "myqrcodemenu.com" in src or src.startswith(BASE_URL):
            assets.append(src)
    
    # CSS
    for tag in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
        href = tag.get("href", "")
        if href.startswith("//"):
            href = "https:" + href
        if not href.startswith("http"):
            href = urljoin(BASE_URL, href)
        if "myqrcodemenu.com" in href or not href.startswith("http"):
            assets.append(href)
    
    # Images
    for tag in soup.find_all("img", src=True):
        src = tag["src"]
        if "{{" in src:
            continue
        if not src.startswith("http"):
            src = urljoin(BASE_URL, src)
        if "myqrcodemenu.com" in src:
            assets.append(src)
    
    for asset_url in set(assets):
        save_path = url_to_path(asset_url, base_dir)
        save_file(asset_url, save_path)
    
    return soup

def get_all_product_images(html):
    """Parse HTML to find all product image paths used in Angular templates"""
    # Look for /files/ paths in the HTML source
    pattern = r'/files/[^\s\'"<>)]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)'
    matches = re.findall(pattern, html, re.IGNORECASE)
    return list(set(matches))

# ── MAIN ──────────────────────────────────────────────────────────────────────

print("=" * 60)
print("The Churroll Caddebostan - Menü İndirici")
print("=" * 60)

os.makedirs(SAVE_DIR, exist_ok=True)

# 1. Ana sayfa
print("\n[1] Ana sayfa indiriliyor...")
r = requests.get(MENU_URL, headers=HEADERS, timeout=30)
html_main = r.text

# HTML'yi kaydet
with open(os.path.join(SAVE_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(html_main)
print("  [OK] index.html")

# Asset'leri indir
print("\n[2] Asset'ler indiriliyor...")
soup = download_page_assets(html_main, MENU_URL, SAVE_DIR)

# 3. Kategori sayfaları
print("\n[3] Kategori sayfaları indiriliyor...")
all_product_images = []
for cat_name, cat_id in CATEGORIES:
    cat_url = f"{MENU_URL}/categories/{cat_id}"
    print(f"  Kategori: {cat_name}")
    try:
        r = requests.get(cat_url, headers=HEADERS, timeout=30)
        cat_html = r.text
        cat_dir = os.path.join(SAVE_DIR, "menu", MENU_SLUG, "tr", "categories")
        os.makedirs(cat_dir, exist_ok=True)
        with open(os.path.join(cat_dir, f"{cat_id}.html"), "w", encoding="utf-8") as f:
            f.write(cat_html)
        
        # Ürün resimlerini bul
        imgs = get_all_product_images(cat_html)
        all_product_images.extend(imgs)
        print(f"    {len(imgs)} ürün resmi bulundu")
        time.sleep(0.3)
    except Exception as e:
        print(f"    HATA: {e}")

# Ana sayfadan da resim bul
all_product_images.extend(get_all_product_images(html_main))
all_product_images = list(set(all_product_images))

# 4. Ürün resimlerini indir
print(f"\n[4] {len(all_product_images)} ürün resmi indiriliyor...")
for img_path in all_product_images:
    full_url = BASE_URL + img_path
    save_path = url_to_path(full_url, SAVE_DIR)
    save_file(full_url, save_path)

# 5. Favicon ve logo'ları indir
print("\n[5] Logo ve favicon'lar indiriliyor...")
favicon_paths = [
    "/img/favicons/apple-icon-57x57.png",
    "/img/favicons/apple-icon-60x60.png",
    "/img/favicons/apple-icon-72x72.png",
    "/img/favicons/apple-icon-76x76.png",
    "/img/favicons/apple-icon-114x114.png",
    "/img/favicons/apple-icon-120x120.png",
    "/img/favicons/apple-icon-144x144.png",
    "/img/favicons/apple-icon-152x152.png",
    "/img/favicons/apple-icon-180x180.png",
    "/img/favicons/android-icon-192x192.png",
    "/img/favicons/favicon-32x32.png",
    "/img/favicons/favicon-96x96.png",
    "/img/favicons/favicon-16x16.png",
    "/img/product-mock.jpg",
    "/img/favicons/manifest.json",
]
for p in favicon_paths:
    save_file(BASE_URL + p, url_to_path(BASE_URL + p, SAVE_DIR))

# 6. Logo dosyaları - HTML'den bulduklarımız
print("\n[6] Restoran logosu ve kategori görselleri...")
logo_pattern = r'/files/(?:logos|categories|products)/[^\s\'\"<>)]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)'
all_imgs = re.findall(logo_pattern, html_main, re.IGNORECASE)
for img_path in set(all_imgs):
    if "{{" not in img_path:
        save_file(BASE_URL + img_path, url_to_path(BASE_URL + img_path, SAVE_DIR))

# 7. CSS'den URL referanslarını bul
css_path = os.path.join(SAVE_DIR, "assets", "menu-detail")
if os.path.exists(css_path):
    for f in os.listdir(css_path):
        if f.endswith(".css"):
            with open(os.path.join(css_path, f), "r", encoding="utf-8", errors="ignore") as cf:
                css_content = cf.read()
            urls_in_css = re.findall(r'url\(["\']?(/[^)"\'>]+)["\']?\)', css_content)
            for u in urls_in_css:
                full_url = BASE_URL + u
                save_file(full_url, url_to_path(full_url, SAVE_DIR))

print("\n" + "=" * 60)
print("İndirme tamamlandı!")
print(f"Dosyalar: {SAVE_DIR}")
print("=" * 60)

# Özet
total_files = sum(len(files) for _, _, files in os.walk(SAVE_DIR))
total_size = sum(
    os.path.getsize(os.path.join(r, f))
    for r, _, files in os.walk(SAVE_DIR) for f in files
)
print(f"Toplam dosya: {total_files}")
print(f"Toplam boyut: {total_size / 1024 / 1024:.1f} MB")
