#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path("index.html")
page = INDEX.read_text(encoding="utf-8")

GOOGLE_REVIEW_URL = "https://www.google.com/maps/search/?api=1&query=Kerem+Gorgulu+REB365+Plano+TX"
ZILLOW_REVIEW_URL = "https://www.zillow.com/profile/keremgorgulu"

block = f'''<!-- REVIEW_CTA_START -->
    <div class="reveal" style="margin:28px 0 36px;">
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;">
        <div style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:var(--shadow-card);text-align:center;">
          <div style="font-size:28px;margin-bottom:8px;">★★★★★</div>
          <h3 style="font-size:23px;margin-bottom:8px;">Leave a Google Review</h3>
          <p style="color:var(--ink-soft);font-size:14px;margin-bottom:18px;">Worked with Kerem? Share your experience on Google to help future North Texas buyers and sellers.</p>
          <a href="{GOOGLE_REVIEW_URL}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" aria-label="Leave Kerem Gorgulu a Google review">Leave a Google Review →</a>
        </div>
        <div style="background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px;box-shadow:var(--shadow-card);text-align:center;">
          <div style="font-size:28px;margin-bottom:8px;">★★★★★</div>
          <h3 style="font-size:23px;margin-bottom:8px;">Leave a Zillow Review</h3>
          <p style="color:var(--ink-soft);font-size:14px;margin-bottom:18px;">Kerem currently has a 5.0-star Zillow profile. Add your own review directly from his Zillow agent page.</p>
          <a href="{ZILLOW_REVIEW_URL}" target="_blank" rel="noopener noreferrer" class="btn btn-light" style="border:1px solid var(--line);" aria-label="Leave Kerem Gorgulu a Zillow review">Leave a Zillow Review →</a>
        </div>
      </div>
      <p style="text-align:center;color:var(--ink-soft);font-size:12px;margin-top:14px;">Reviews should reflect your genuine experience. Google and Zillow each apply their own review policies.</p>
    </div>
<!-- REVIEW_CTA_END -->'''

managed = re.compile(r'<!-- REVIEW_CTA_START -->.*?<!-- REVIEW_CTA_END -->', re.S)
if managed.search(page):
    page = managed.sub(block, page)
else:
    marker = '    <div class="review-grid">'
    if marker not in page:
        raise SystemExit("Testimonials review grid not found; refusing unverified edit")
    page = page.replace(marker, block + "\n\n" + marker, 1)

INDEX.write_text(page, encoding="utf-8")
print("Google and Zillow review CTAs added/updated.")
