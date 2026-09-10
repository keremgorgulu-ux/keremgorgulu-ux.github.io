#!/usr/bin/env python3
from pathlib import Path
import html as htmlmod
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

HAR = "https://www.har.com/kerem-gorgulu/agent_ntreis-0717217"
INDEX = Path("index.html")
FIXED_SOLD = "55"

resp = requests.get(HAR, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")
text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))
page = INDEX.read_text(encoding="utf-8")

def count(label):
    # Prefer the agent-profile summary links, e.g. "3 For Sale" / "3 For Rent".
    for a in soup.find_all("a"):
        t = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
        m = re.fullmatch(rf"(\d+)\s+{re.escape(label)}", t, re.I)
        if m:
            return m.group(1)
    # Fallback for HAR markup changes.
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

# Preserve owner-selected marketing count.
page = re.sub(r'data-count="\d+" data-suffix="">0</b><span>Homes Sold', f'data-count="{FIXED_SOLD}" data-suffix="">0</b><span>Homes Sold', page)
page = re.sub(r'with \d+ homes sold and a', f'with {FIXED_SOLD} homes sold and a', page)
page = re.sub(r'(reviews on Zillow · )\d+( homes sold)', rf'\g<1>{FIXED_SOLD}\2', page)
page = page.replace('Free for buyers · commission paid by seller','Buyer representation fees are negotiable · compensation varies by transaction')

# Extract active property cards from the public HAR profile.
# Do NOT assume an address starts with a number: land / lot listings can begin with TBD, Lot, etc.
active = []
seen = set()
for a in soup.find_all("a", href=True):
    label = re.sub(r"\s+", " ", a.get_text(" ", strip=True)).strip()
    if not label or len(label) > 140:
        continue
    container = a
    matched = False
    for _ in range(7):
        if not container.parent:
            break
        container = container.parent
        chunk = re.sub(r"\s+", " ", container.get_text(" ", strip=True))
        if " Active " in f" {chunk} " and re.search(r"\d+\s+beds?", chunk, re.I) and re.search(r"\d+\s+baths?", chunk, re.I) and re.search(r"[\d,]+\s+sqft", chunk, re.I):
            matched = True
            break
    if not matched:
        continue
    chunk = re.sub(r"\s+", " ", container.get_text(" ", strip=True))
    m_city = re.search(r"([A-Za-z .'-]+),\s*TX\s+(\d{5})", chunk)
    m_price = re.search(r"(\$[\d.,]+\s*[KkMm]?)", chunk)
    m_bed = re.search(r"(\d+)\s+beds?", chunk, re.I)
    m_bath = re.search(r"(\d+)\s+baths?", chunk, re.I)
    m_sqft = re.search(r"([\d,]+)\s+sqft", chunk, re.I)
    if not (m_city and m_price and m_bed and m_bath and m_sqft):
        continue

    # Prefer a label that looks like the property address, but permit non-numbered addresses.
    bad_labels = {"active", "for sale", "for rent", "view details", "details", "map", "list view", "map view"}
    if label.lower() in bad_labels or label.startswith("$"):
        continue

    key = (label.lower(), m_city.group(2))
    if key in seen:
        continue
    seen.add(key)
    active.append({
        "address": label,
        "city": m_city.group(1).strip(),
        "zip": m_city.group(2),
        "price": m_price.group(1).replace(" ", ""),
        "beds": m_bed.group(1),
        "baths": m_bath.group(1),
        "sqft": m_sqft.group(1),
        "url": urljoin(HAR, a["href"]),
    })

expected = int(for_sale or 0) + int(for_rent or 0)
if expected and len(active) < expected:
    raise SystemExit(f"HAR shows {expected} active listings but only {len(active)} were parsed; refusing partial update. Parsed: {[x['address'] for x in active]}")
active = active[:expected] if expected else active

sale_count = int(for_sale or 0)
for i, item in enumerate(active):
    item["type"] = "For Sale" if i < sale_count else "For Rent"

cards = []
for item in active:
    rental = item["type"] == "For Rent"
    price = htmlmod.escape(item["price"]) + (" / mo" if rental else "")
    cards.append(f'''<article class="listing-card reveal har-listing-card">
  <div class="listing-body">
    <span class="listing-tag" style="position:static;display:inline-block;margin-bottom:12px;">{htmlmod.escape(item['type'])}</span>
    <div class="listing-price">{price}</div>
    <div class="listing-addr">{htmlmod.escape(item['address'])}, {htmlmod.escape(item['city'])}, TX {item['zip']}</div>
    <div class="listing-meta"><span>🛏 {item['beds']} beds</span><span>🛁 {item['baths']} baths</span><span>📐 {item['sqft']} sqft</span></div>
    <a href="{htmlmod.escape(item['url'], quote=True)}" target="_blank" rel="noopener noreferrer" class="btn btn-ghost" style="margin-top:18px;padding:11px 18px;font-size:13px;">View on HAR →</a>
  </div>
</article>''')

listing_section = f'''<!-- HAR_LISTINGS_START -->
<section class="listings" id="listings">
  <div class="wrap">
    <div class="section-head center reveal">
      <span class="eyebrow" style="justify-content:center;">My Active Listings</span>
      <h2>Current homes for sale &amp; rent</h2>
      <p>Live inventory from Kerem Gorgulu's public HAR profile. Click any property for the latest listing details.</p>
    </div>
    <div class="listing-grid">{''.join(cards)}</div>
    <div class="listings-foot"><a href="{HAR}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">View All My HAR Listings →</a></div>
  </div>
</section>
<!-- HAR_LISTINGS_END -->'''

managed = re.compile(r'<!-- HAR_LISTINGS_START -->.*?<!-- HAR_LISTINGS_END -->', re.S)
if managed.search(page):
    page = managed.sub(listing_section, page)
else:
    anchor = '<!-- ================= PROBLEM / SOLUTION ================= -->'
    if anchor not in page:
        raise SystemExit('Expected insertion anchor not found; refusing to modify index.html')
    page = page.replace(anchor, listing_section + '\n\n' + anchor, 1)

# Once the local listings section exists, all Listings buttons should scroll to it.
page = re.sub(r'href="https://www\.har\.com/kerem-gorgulu/agent_ntreis-0717217"\s+target="_blank"\s+rel="noopener noreferrer"(?=[^>]*>Listings<)', 'href="#listings"', page)
page = re.sub(r'href="https://www\.har\.com/kerem-gorgulu/agent_ntreis-0717217"\s+target="_blank"\s+rel="noopener noreferrer"(?=[^>]*>See Current Listings<)', 'href="#listings"', page)

status = f'''<!-- HAR_STATUS_START -->
<div class="wrap" style="padding-top:22px;padding-bottom:22px;text-align:center;font-size:14px;color:var(--ink-soft);">
  Current HAR activity: <strong>{for_sale or '—'} for sale</strong> · <strong>{for_rent or '—'} for rent</strong> · <strong>{rented or '—'} rented records</strong> · <a href="{HAR}" target="_blank" rel="noopener" style="color:var(--terracotta);font-weight:700;">View HAR profile →</a>
</div>
<!-- HAR_STATUS_END -->'''
status_managed = re.compile(r'<!-- HAR_STATUS_START -->.*?<!-- HAR_STATUS_END -->', re.S)
if status_managed.search(page):
    page = status_managed.sub(status, page)

INDEX.write_text(page, encoding="utf-8")
print(f"Updated {len(active)} active HAR listings; for_sale={for_sale}, for_rent={for_rent}, rented={rented}; fixed headline sold={FIXED_SOLD}")
