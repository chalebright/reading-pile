# readwise_export.py
import os, sys, json, pathlib, re, requests, datetime, unicodedata

OUT = pathlib.Path("ReadingMem")
OUT.mkdir(exist_ok=True)

TOKEN = os.getenv("READWISE_TOKEN")
if not TOKEN:
    print("Set READWISE_TOKEN"); sys.exit(1)

def slugify(s):
    s = unicodedata.normalize('NFKD', s or "untitled").encode('ascii','ignore').decode('ascii')
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def get_since():
    f = OUT / "last_sync.txt"
    return f.read_text().strip() if f.exists() else None

def save_since(ts_iso):
    (OUT / "last_sync.txt").write_text(ts_iso)

def fetch_export(updated_after=None):
    url = "https://readwise.io/api/v2/export/"
    headers = {"Authorization": f"Token {TOKEN}"}
    params = {}
    if updated_after:
        params["updatedAfter"] = updated_after
    results = []
    while True:
        r = requests.get(url, headers=headers, params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        results.extend(data.get("results", []))
        cur = data.get("nextPageCursor")
        if not cur: break
        params = {"pageCursor": cur}
    return results

def normalize_book(b):
    def tag_names(t):
        if isinstance(t, list) and t and isinstance(t[0], dict):
            return [x.get("name","").strip() for x in t]
        return t or []
    book_id = f'{b["user_book_id"]}-{slugify(b.get("title"))[:50]}'
    highlights = []
    for h in b.get("highlights", []):
        highlights.append({
            "id": h["id"],
            "loc": {
                "type": h.get("location_type"),
                "value": h.get("location"),
                "end": h.get("end_location")
            },
            "text": h.get("text"),
            "note": h.get("note"),
            "tags": tag_names(h.get("tags")),
            "created_at": h.get("highlighted_at"),
            "readwise_url": h.get("readwise_url")
        })
    return {
        "book_id": book_id,
        "title": b.get("title"),
        "author": b.get("author"),
        "source": b.get("source"),
        "readwise_url": b.get("readwise_url"),
        "category": b.get("category"),
        "highlights": highlights
    }

def main():
    since = get_since()
    books = fetch_export(since)
    index = []
    for b in books:
        nb = normalize_book(b)
        fn = OUT / f'{nb["book_id"]}.json'
        fn.write_text(json.dumps(nb, ensure_ascii=False, indent=2), encoding="utf-8")
        index.append({"book_id": nb["book_id"], "title": nb["title"], "author": nb["author"], "file": fn.name})
    # merge with previous index
    idx_file = OUT / "index.json"
    if idx_file.exists():
        try:
            old = json.loads(idx_file.read_text(encoding="utf-8"))
        except Exception:
            old = []
        existing = {x["book_id"]: x for x in old}
        for x in index:
            existing[x["book_id"]] = x
        index = list(existing.values())
    idx_file.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    save_since(datetime.datetime.utcnow().isoformat()+"Z")
    print(f"Wrote {len(books)} updated books. Total index: {len(index)}")

if __name__ == "__main__":
    main()
