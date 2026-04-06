import requests, re, json, os
from html import unescape

BASE_URL = "https://menu.myqrcodemenu.com"
MENU_SLUG = "the-churroll-caddebostan-193bcd"
SAVE_DIR = r"C:\Users\ByMED\Desktop\Qr Churroll\site"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept-Language": "tr-TR,tr;q=0.9"}

CATEGORIES = [
    ("Churros",         "a9064814-8e51-44a9-8048-fd97291d83d1"),
    ("Sıcak İçecekler", "65ff6611-aab2-4234-a662-53a5f25accb0"),
    ("Soğuk İçecekler", "4dd5330a-5020-4275-bf91-efefa2147af4"),
    ("Ekstralar",       "aa7462f5-1ad8-4a95-a1cf-efea8721b65c"),
]

def save_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if os.path.exists(save_path):
        print(f"  [EXISTS] {os.path.basename(save_path)[:60]}")
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(r.content)
            print(f"  [OK] {os.path.basename(save_path)[:60]}")
            return True
        else:
            print(f"  [SKIP {r.status_code}] {url}")
            return False
    except Exception as e:
        print(f"  [ERR] {e}")
        return False

all_products = []

for cat_name, cat_id in CATEGORIES:
    url = f"{BASE_URL}/menu/{MENU_SLUG}/tr/categories/{cat_id}"
    print(f"\n=== {cat_name} ===")
    r = requests.get(url, headers=HEADERS, timeout=30)
    html = r.text

    # Extract JSON from openProductDetailPopup calls (HTML entity encoded)
    # Pattern: openProductDetailPopup('{"LangId":...}', link, pos)
    raw_jsons = re.findall(r"openProductDetailPopup\('(\{[^']+\})'", html)
    if not raw_jsons:
        # Try with HTML entities
        raw_jsons = re.findall(r'openProductDetailPopup\(&#x27;(\{[^<]+\})&#x27;', html)
    if not raw_jsons:
        # Try decoded version
        decoded_html = unescape(html)
        raw_jsons = re.findall(r"openProductDetailPopup\('(\{[^']+\})'", decoded_html)

    products_in_cat = []
    for raw in raw_jsons:
        try:
            decoded = unescape(raw)
            prod = json.loads(decoded)
            products_in_cat.append(prod)
            pic = prod.get("ProductPicture", "")
            name = prod.get("ProductName", "?")
            price = prod.get("ProductPrice", "?")
            print(f"  - {name} ({price} TL) | pic: {pic[:50] if pic else 'yok'}")
        except Exception as e:
            print(f"  PARSE ERR: {e} | raw: {raw[:100]}")

    all_products.extend(products_in_cat)

    # Also look for img tags with files/products
    imgs = re.findall(r'src=["\']([^"\']*files/products/[^"\']+)["\']', html)
    for img in imgs:
        if "{{" not in img:
            full = BASE_URL + img if img.startswith("/") else img
            fname = img.split("/files/products/")[-1]
            local = os.path.join(SAVE_DIR, "files", "products", fname)
            save_file(full, local)

print(f"\n\nToplam {len(all_products)} ürün bulundu")

# Save all products as JSON for reference
with open(os.path.join(SAVE_DIR, "menu_products.json"), "w", encoding="utf-8") as f:
    json.dump(all_products, f, ensure_ascii=False, indent=2)
print("menu_products.json kaydedildi")

# Download pictures
print("\nResimler indiriliyor...")
for prod in all_products:
    pic = prod.get("ProductPicture", "")
    if pic and "{{" not in pic:
        if not pic.startswith("http"):
            url = f"{BASE_URL}/files/products/{pic}"
        else:
            url = pic
        fname = pic.split("/")[-1] if "/" in pic else pic
        local = os.path.join(SAVE_DIR, "files", "products", fname)
        save_file(url, local)

total_files = sum(len(files) for _, _, files in os.walk(SAVE_DIR))
total_size = sum(os.path.getsize(os.path.join(rr, f)) for rr, _, files in os.walk(SAVE_DIR) for f in files)
print(f"\nToplam: {total_files} dosya | {total_size/1024/1024:.1f} MB")
