# KG Realty rental marketplace setup

This GitHub Pages frontend provides public search, owner listing submissions, tenant applications, application status and application-based messaging. A fresh Supabase project supplies passwordless authentication and a database with row-level access controls. It does **not** collect SSNs, screening reports, rent, deposits or listing payments.

## Activate the account workflow

1. Create a Supabase project controlled by the brokerage/operator. In SQL Editor run `supabase/schema.sql`. Use a staging project first.
2. In Authentication → URL Configuration set the Site URL to `https://kgrealty.it.com/rentals.html`. Add this URL and `https://keremgorgulu-ux.github.io/rentals.html` to redirect allowlist. Enable email OTP and configure reliable SMTP for production.
3. Copy the project's public URL and **publishable/anon key** into `rental-config.js`. Never paste the `service_role` key, payment secret or screening credentials in GitHub.
4. Verify with two separate test users: submit an owner listing, publish it from Supabase Table Editor after review, apply as a tenant, update the status as the owner, exchange messages, and confirm unrelated users cannot read applications or messages.
5. Publish only after brokerage approval of advertising, listing terms, fees, tenant selection criteria, data handling, and payment arrangements. Provide a privacy notice and retention/deletion procedure before inviting real applicants.

A new listing starts as `pending`. A staff member reviews ownership/authorization and listing terms and changes `status` to `published` in the Supabase Table Editor. Applicants can then see it. Tenant applications capture name, contact and introduction only. Do not request sensitive screening details in free-text fields or chat.

## Payments and screening

- **Listing fee:** Set an agreed flat fee and written scope with the sponsoring brokerage, then create a brokerage-controlled checkout using a provider such as Stripe. Confirm payment through a signed webhook in a server environment before automatic publication. A payment link alone is insufficient proof of payment and is intentionally absent from this prototype.
- **Rent and owner payouts:** Select a brokerage-approved property management system supporting tenant payments, owner ledgers, deposits and disbursements. Put its resident login URL in `rentPortalUrl` only when the portal is live. The public site must never collect card or bank details. Do not send rent to a personal Stripe account.
- **Credit/background checks:** Select a tenant-screening provider with permissible-purpose verification, applicant authorization, secure identity collection, report handling, dispute process and adverse-action workflow. Integrate that provider's hosted invitation/API on the server side; never run credit checks from browser JavaScript or store reports in this database.
- **Owner decisions:** The status control records a decision but does not issue required notices. Complete appropriate notices through the approved screening process when using a consumer report.

## Feature boundary

The account dashboard supports a listing application and a conversation tied to that application. It does not yet include uploaded photos, identity verification, lease signing, maintenance requests, financial statements, automated listing-fee checkout, credit scores, background checks or rent collection. Photo entries currently accept an HTTPS image URL. Keep the existing property management page's full-service portals marked “coming soon” until a management provider is live.

For a production launch, add a backend for payment webhooks and screening invitations, email notifications, moderation, spam controls, audit logs, consent records, and a privacy/retention policy. Review accessibility and the hosting provider's terms for storing applicant data.
