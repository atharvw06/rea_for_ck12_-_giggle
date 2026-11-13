import urllib.request
import re
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.ck12.org/assessment/ui/browse/practice/life-science/?topicHandle=foundations-of-life-science',
    'Accept': 'application/json, text/javascript, */*; q=0.01'
}

def query_taxonomy(branch="life-science"):
    url = f"https://www.ck12.org/flx/get/info/browseTerm/descendants/{branch}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def query_modality_practice(topic="foundations-of-life-science"):
    url = f"https://www.ck12.org/flx/search/direct/modality/minimal/asmtpractice/{topic}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))

if __name__ == "__main__":
    print("Testing CK-12 Taxonomy API...")
    tax = query_taxonomy()
    term = tax.get("response", {}).get("term", {})
    print(f"Branch: {term.get('name')} (Handle: {term.get('handle')}, EncodedID: {term.get('encodedID')})")

    print("\nTesting CK-12 Modality Practice API...")
    mod = query_modality_practice()
    artifacts = mod.get("response", {}).get("Artifacts", {}).get("result", [])
    print(f"Retrieved {len(artifacts)} practice artifact modules.")
