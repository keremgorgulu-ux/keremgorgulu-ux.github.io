#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path("index.html")
page = INDEX.read_text(encoding="utf-8")

# Use the repository-hosted image for both 2507 Gentle Knoll cards.
# This avoids hotlink failures and oversized/broken data URIs.
local_photo = "assets/listings/2507-gentle-knoll-dr.jpg"
pattern = re.compile(
    r'(<img\s+class="har-listing-photo"\s+src=")[^"]*("\s+alt="2507 Gentle Knoll Dr, Melissa, TX 75454"[^>]*>)',
    re.IGNORECASE,
)
page, count = pattern.subn(r'\1' + local_photo + r'\2', page)

if count == 0:
    raise SystemExit("2507 Gentle Knoll listing image tags were not found; refusing an unverified patch")

INDEX.write_text(page, encoding="utf-8")
print(f"Set {count} Gentle Knoll listing card image(s) to {local_photo}")
