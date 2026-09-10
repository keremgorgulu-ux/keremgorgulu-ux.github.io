#!/usr/bin/env python3
from pathlib import Path

INDEX = Path("index.html")
page = INDEX.read_text(encoding="utf-8")

# 821 Field Xing: verified current Zillow primary image for the exact property.
wrong = "https://photos.zillowstatic.com/fp/07eca0888e90bee720ecfeed342335a5-cc_ft_960.jpg"
correct = "https://photos.zillowstatic.com/fp/6ffff89b4105976dfc105b17ac2a59d1-cc_ft_960.jpg"

if wrong in page:
    page = page.replace(wrong, correct)
elif correct not in page:
    raise SystemExit("821 Field Xing listing card image URL was not found; refusing an unverified patch")

INDEX.write_text(page, encoding="utf-8")
print("Verified 821 Field Xing main photo URL.")
