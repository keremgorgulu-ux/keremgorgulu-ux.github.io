#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path("index.html")
page = INDEX.read_text(encoding="utf-8")

replacements = [
    (
        "2507 Gentle Knoll Dr, Melissa, TX 75454",
        "assets/listings/2507-gentle-knoll-dr.jpg?v=20260910-2",
    ),
    (
        "10492 US Highway 69, Whitewright, TX 75491",
        "assets/listings/10492-us-highway-69.jpg?v=20260910-1",
    ),
]

updated = 0
for alt_text, local_photo in replacements:
    pattern = re.compile(
        rf'(<img\s+class="har-listing-photo"\s+src=")[^"]*("\s+alt="{re.escape(alt_text)}"[^>]*>)',
        re.IGNORECASE,
    )
    page, count = pattern.subn(r'\1' + local_photo + r'\2', page)
    if count == 0:
        raise SystemExit(f"Listing image tag not found for {alt_text}; refusing an unverified patch")
    updated += count

INDEX.write_text(page, encoding="utf-8")
print(f"Updated {updated} listing card image(s) to reliable repository-hosted photos")
