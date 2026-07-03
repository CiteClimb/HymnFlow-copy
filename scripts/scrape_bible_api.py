import os
import json
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# List of 66 books and their canonical chapter counts
BOOKS = [
    ("genesis", 50, "GEN"),
    ("exodus", 40, "EXO"),
    ("leviticus", 27, "LEV"),
    ("numbers", 36, "NUM"),
    ("deuteronomy", 34, "DEU"),
    ("joshua", 24, "JOS"),
    ("judges", 21, "JDG"),
    ("ruth", 4, "RUT"),
    ("1samuel", 31, "1SA"),
    ("2samuel", 24, "2SA"),
    ("1kings", 22, "1KI"),
    ("2kings", 25, "2KI"),
    ("1chronicles", 29, "1CH"),
    ("2chronicles", 36, "2CH"),
    ("ezra", 10, "EZR"),
    ("nehemiah", 13, "NEH"),
    ("esther", 10, "EST"),
    ("job", 42, "JOB"),
    ("psalms", 150, "PSA"),
    ("proverbs", 31, "PRO"),
    ("ecclesiastes", 12, "ECC"),
    ("songofsolomon", 8, "SNG"),
    ("isaiah", 66, "ISA"),
    ("jeremiah", 52, "JER"),
    ("lamentations", 5, "LAM"),
    ("ezekiel", 48, "EZK"),
    ("daniel", 12, "DAN"),
    ("hosea", 14, "HOS"),
    ("joel", 3, "JOL"),
    ("amos", 9, "AMO"),
    ("obadiah", 1, "OBA"),
    ("jonah", 4, "JON"),
    ("micah", 7, "MIC"),
    ("nahum", 3, "NAH"),
    ("habakkuk", 3, "HAB"),
    ("zephaniah", 3, "ZEP"),
    ("haggai", 2, "HAG"),
    ("zechariah", 14, "ZEC"),
    ("malachi", 4, "MAL"),
    ("matthew", 28, "MAT"),
    ("mark", 16, "MRK"),
    ("luke", 24, "LUK"),
    ("john", 21, "JHN"),
    ("acts", 28, "ACT"),
    ("romans", 16, "ROM"),
    ("1corinthians", 16, "1CO"),
    ("2corinthians", 13, "2CO"),
    ("galatians", 6, "GAL"),
    ("ephesians", 6, "EPH"),
    ("philippians", 4, "PHP"),
    ("colossians", 4, "COL"),
    ("1thessalonians", 5, "1TH"),
    ("2thessalonians", 3, "2TH"),
    ("1timothy", 6, "1TI"),
    ("2timothy", 4, "2TI"),
    ("titus", 3, "TIT"),
    ("philemon", 1, "PHM"),
    ("hebrews", 13, "HEB"),
    ("james", 5, "JAS"),
    ("1peter", 5, "1PE"),
    ("2peter", 3, "2PE"),
    ("1john", 5, "1JN"),
    ("2john", 1, "2JN"),
    ("3john", 1, "3JN"),
    ("jude", 1, "JUD"),
    ("revelation", 22, "REV")
]

# Some versions publish books under alternate slugs (e.g. Messianic editions
# use Hebrew names, and a few editions shorten Song of Solomon to "song").
BOOK_SLUG_ALIASES = {
    "songofsolomon": ["song", "songofsongs"],
    "john": ["yochanan"],
    "james": ["jacob"],
    "1john": ["1yochanan"],
    "2john": ["2yochanan"],
    "3john": ["3yochanan"],
    "jude": ["judah"],
}

CACHE_DIR = r"C:\Users\ebenaAdmin\.gemini\antigravity-ide\brain\1954c514-68c7-4cd3-9cd0-87d8e843d8db\scratch\cache_bible_api"
OUTPUT_DIR = r"c:\dev\HymnFlow\public\data"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_url_with_retry(url, retries=5, backoff=1.5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                # Do not retry on 404 Not Found
                raise e
            if i == retries - 1:
                raise e
            time.sleep(backoff * (i + 1))
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(backoff * (i + 1))

def download_chapter(version, book, chapter):
    cache_path = os.path.join(CACHE_DIR, version, f"{book}_{chapter}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass # Re-download if corrupted
            
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)

    last_err = None
    for slug in [book] + BOOK_SLUG_ALIASES.get(book, []):
        url = f"https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/{version}/books/{slug}/chapters/{chapter}.json"
        try:
            data = fetch_url_with_retry(url)
            parsed = json.loads(data.decode('utf-8'))
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, ensure_ascii=False)
            return parsed
        except Exception as e:
            last_err = e

    print(f"Failed to fetch {version} {book} {chapter}: {last_err}")
    return None

# Verified corrections for known upstream defects. The en-rv source drops any
# text following a mid-verse "Selah" (and a trailing verse-final "Selah").
# Replacement texts transcribed from the RV 1885 at biblehub.com/erv.
PATCHES = {
    "en-rv": {
        ("PSA", 55, 19): "God shall hear, and answer them, even he that abideth of old, Selah the men who have no changes, and who fear not God.",
        ("PSA", 57, 3): "He shall send from heaven, and save me, when he that would swallow me up reproacheth; Selah God shall send forth his mercy and his truth.",
        ("HAB", 3, 3): "God came from Teman, and the Holy One from mount Paran. Selah His glory covered the heavens, and the earth was full of his praise.",
        ("HAB", 3, 9): "Thy bow was made quite bare; the oaths to the tribes were a sure word. Selah Thou didst cleave the earth with rivers.",
        ("HAB", 3, 13): "Thou wentest forth for the salvation of thy people, for the salvation of thine anointed; thou woundedst the head out of the house of the wicked, laying bare the foundation even unto the neck. Selah",
    },
}

# en-kjv appends marginal notes to verse text as "<ch>.<v> note text..." with no
# delimiter. Genuine KJV verse text never contains digits (numbers are spelled
# out), so stripping from the first digit-dot-digit marker removes exactly the
# note apparatus. Pilcrows are paragraph marks, unwanted for projection.
KJV_NOTE_RE = re.compile(r'\s*(?<![0-9])\d+\.\d+(?![0-9]).*$', re.S)

def clean_verse_text(version_id, text):
    if version_id == "en-kjv":
        text = KJV_NOTE_RE.sub('', text)
        text = text.replace('¶', '').strip()
    return text

def process_version(version_info):
    version_id = version_info["id"]
    version_name = version_info["version"]
    print(f"\nProcessing version: {version_id} ({version_name})")
    
    # We want to collect all download tasks
    tasks = []
    for book, chapters_count, code in BOOKS:
        for ch in range(1, chapters_count + 1):
            tasks.append((version_id, book, ch, code))
            
    # Download concurrently
    results = {}
    success_count = 0
    
    # Using 30 workers for fast concurrency without overloading CDN
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(download_chapter, vid, bk, ch): (bk, ch, code) for vid, bk, ch, code in tasks}
        
        for idx, future in enumerate(as_completed(futures)):
            bk, ch, code = futures[future]
            try:
                res = future.result()
                if res and "data" in res:
                    if code not in results:
                        results[code] = []
                    results[code].append((ch, res["data"]))
                    success_count += 1
            except Exception as e:
                print(f"Error in future result: {e}")
                
            if (idx + 1) % 100 == 0 or (idx + 1) == len(tasks):
                print(f"  Progress: {idx + 1}/{len(tasks)} chapters processed.")

    if success_count < len(tasks):
        print(f"WARNING: Only downloaded {success_count}/{len(tasks)} chapters for {version_id}.")
        # If we failed to download any chapters, skip
        if success_count == 0:
            print(f"SKIPPING output generation for {version_id} because no chapters were downloaded.")
            return

    # Structure into HymnFlow format
    # Structure: { CODE: { name: canonical_name, chapters: [null, [null, "v1", "v2", ...], ...] } }
    hymnflow_data = {}
    for book, chapters_count, code in BOOKS:
        # Get book name (we can get from data or fall back to canonical)
        # Find any successfully parsed chapter to extract actual book name if available
        real_name = book.capitalize()
        ch_list = results.get(code, [])
        if ch_list:
            first_ch_verses = ch_list[0][1]
            if first_ch_verses:
                real_name = first_ch_verses[0].get("book", real_name)
                
        # Prepare chapters list: index 0 is None
        chapters_1indexed = [None]
        
        # Sort chapters by chapter number
        ch_sorted = sorted(ch_list, key=lambda x: x[0])
        
        # We need to fill in chapters. If some chapters are missing (e.g. 404 or transient error),
        # fill with empty verses list so it doesn't crash the index lookup.
        ch_dict = {ch_num: verses for ch_num, verses in ch_sorted}
        
        for ch in range(1, chapters_count + 1):
            verses_data = ch_dict.get(ch, [])
            # Place each verse at its actual verse-number index. Some source
            # versions repeat every verse entry (identical copies), so keep
            # only the first occurrence per verse number.
            verses_texts = [None]
            for v in verses_data:
                try:
                    n = int(v["verse"])
                except (KeyError, ValueError, TypeError):
                    continue
                if n < 1:
                    continue
                while len(verses_texts) <= n:
                    verses_texts.append("")
                if verses_texts[n] == "":
                    verses_texts[n] = clean_verse_text(version_id, v.get("text", ""))
            chapters_1indexed.append(verses_texts)
            
        hymnflow_data[code] = {
            "name": real_name,
            "chapters": chapters_1indexed
        }

    for (code, ch, vs), text in PATCHES.get(version_id, {}).items():
        try:
            hymnflow_data[code]["chapters"][ch][vs] = text
        except (KeyError, IndexError):
            print(f"WARNING: patch target {code} {ch}:{vs} not found in {version_id}")
        
    # Write JSON output
    json_path = os.path.join(OUTPUT_DIR, f"bible-{version_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(hymnflow_data, f, ensure_ascii=False, separators=(",", ":"))
        
    # Write JS output (assign to window.HymnFlowBible for direct script tag loading support)
    js_path = os.path.join(OUTPUT_DIR, f"bible-{version_id}.js")
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(f"window.HymnFlowBible = ")
        json.dump(hymnflow_data, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
        
    print(f"Successfully wrote {json_path} and {js_path}")

def main():
    # Load bibles
    url = "https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles/bibles.json"
    bibles = json.loads(fetch_url_with_retry(url).decode('utf-8'))
        
    # Filter English bibles (starting with en-)
    en_bibles = [b for b in bibles if b["id"].startswith("en-")]
    print(f"Found {len(en_bibles)} English translations:")
    for b in en_bibles:
        print(f"  - {b['id']}: {b['version']}")
        
    for b in en_bibles:
        process_version(b)

if __name__ == "__main__":
    main()
