import urllib.request
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Origin': 'https://giggleacademy.com',
    'Referer': 'https://giggleacademy.com/'
}

def check_apk_download():
    url = "https://creator.giggleacademy.com/api/download/latest-apk?channel=website"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return {
            "resolved_url": resp.geturl(),
            "status": resp.status,
            "content_length": resp.headers.get("Content-Length"),
            "content_type": resp.headers.get("Content-Type")
        }

def query_public_books(topic="all"):
    url = f"https://creator.giggleacademy.com/api/book/public/topic/{topic}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

if __name__ == "__main__":
    print("Checking Giggle APK download endpoint...")
    apk_info = check_apk_download()
    print(json.dumps(apk_info, indent=2))

    print("\nQuerying Giggle public books...")
    books = query_public_books()
    print(json.dumps(books, indent=2))
