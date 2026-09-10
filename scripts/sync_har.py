#!/usr/bin/env python3
from pathlib import Path
import re
import requests

HAR = "https://www.har.com/kerem-gorgulu/agent_ntreis-0717217"
INDEX = Path("index.html")
FIXED_SOLD = "55"

html = INDEX.read_text(encoding="utf-8")
resp = requests.get(HAR, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.raise_for_status()
text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", resp.text))

def count(label):
    for pat in (rf"(\d+)\s+{label}\b", rf"{label}\s+(\d+)\b"):
        m = re.search(pat, text, re.I)
        if m:
            return m.group(1)
    return None

for_sale = count("For Sale")
for_rent = count("For Rent")
rented = count("Rented")
if not any((for_sale, for_rent, rented)):
    raise SystemExit("HAR verification failed; refusing to modify index.html")

html = re.sub(r'data-count="\d+" data-suffix="">0</b><span>Homes Sold', f'data-count="{FIXED_SOLD}" data-suffix="">0</b><span>Homes Sold', html)
html = re.sub(r'with \d+ homes sold and a', f'with {FIXED_SOLD} homes sold and a', html)
html = re.sub(r'(reviews on Zillow · )\d+( homes sold)', rf'\g<1>{FIXED_SOLD}\2', html)
html = html.replace('Free for buyers · commission paid by seller','Buyer representation fees are negotiable · compensation varies by transaction')

# The site does not currently contain a #listings section, so internal My Listings / Listings links were dead.
# Point every #listings link directly to Kerem's verified public HAR inventory instead.
html = html.replace('href="#listings"', f'href="{HAR}" target="_blank" rel="noopener noreferrer"')

strip = f'''<!-- HAR_STATUS_START -->
<div class="wrap" style="padding-top:22px;padding-bottom:22px;text-align:center;font-size:14px;color:var(--ink-soft);">
  Current HAR activity: <strong>{for_sale or '—'} for sale</strong> · <strong>{for_rent or '—'} for rent</strong> · <strong>{rented or '—'} rented records</strong> · <a href="{HAR}" target="_blank" rel="noopener" style="color:var(--terracotta);font-weight:700;">View HAR profile →</a>
</div>
<!-- HAR_STATUS_END -->'''
managed = re.compile(r'<!-- HAR_STATUS_START -->.*?<!-- HAR_STATUS_END -->', re.S)
if managed.search(html):
    html = managed.sub(strip, html)
else:
    anchor = '<!-- ================= PROBLEM / SOLUTION ================= -->'
    if anchor not in html:
        raise SystemExit('Expected insertion anchor not found; refusing to modify index.html')
    html = html.replace(anchor, strip + '\n\n' + anchor, 1)

INDEX.write_text(html, encoding="utf-8")
print(f"Verified HAR: for_sale={for_sale}, for_rent={for_rent}, rented={rented}; fixed headline sold={FIXED_SOLD}; listings links={HAR}")
