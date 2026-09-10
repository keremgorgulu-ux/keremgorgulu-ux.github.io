#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path("index.html")
page = INDEX.read_text(encoding="utf-8")

# 2507 Gentle Knoll Dr: use a local repo image so the card does not depend on
# a remote image host or an oversized inline data URI. This patches both the
# For Sale and For Rent cards for the same property.
gentle_pattern = re.compile(
    r'<img class="har-listing-photo" src="[^"]+" alt="2507 Gentle Knoll Dr, Melissa, TX 75454" loading="lazy">'
)
gentle_replacement = (
    '<img class="har-listing-photo" src="assets/listings/2507-gentle-knoll-dr.jpg" '
    'alt="2507 Gentle Knoll Dr, Melissa, TX 75454" loading="lazy">'
)
page, gentle_count = gentle_pattern.subn(gentle_replacement, page)
if gentle_count < 1:
    raise SystemExit("2507 Gentle Knoll listing card was not found; refusing an unverified patch")

# 821 Field Xing: keep the verified current Zillow primary image.
wrong = "https://photos.zillowstatic.com/fp/07eca0888e90bee720ecfeed342335a5-cc_ft_960.jpg"
correct = "https://photos.zillowstatic.com/fp/6ffff89b4105976dfc105b17ac2a59d1-cc_ft_960.jpg"
if wrong in page:
    page = page.replace(wrong, correct)
elif correct not in page:
    raise SystemExit("821 Field Xing listing card image URL was not found; refusing an unverified patch")

INDEX.write_text(page, encoding="utf-8")
print(f"Fixed 2507 Gentle Knoll local photo on {gentle_count} card(s) and verified 821 Field Xing photo URL.")
