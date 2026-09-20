-- Run in a new Supabase project's SQL editor. Review before production use.
create extension if not exists pgcrypto;
create table if not exists public.rental_listings (
 id uuid primary key default gen_random_uuid(), owner_id uuid not null references auth.users(id),
 address text not null check(length(address) between 3 and 160), city text not null check(length(city) between 2 and 80),
 rent numeric(10,2) not null check(rent between 1 and 100000), beds numeric(4,1) not null check(beds between 0 and 30), baths numeric(4,1) not null check(baths between 0 and 30),
 sqft integer check(sqft between 1 and 100000), description text not null check(length(description) between 10 and 3000),
 photo_url text check(photo_url is null or (length(photo_url)<1500 and photo_url ~ '^https://')),
 available_on date, status text not null default 'pending' check(status in ('pending','published','rejected','leased')),
 created_at timestamptz not null default now()
);
create table if not exists public.rental_applications (
 id uuid primary key default gen_random_uuid(), listing_id uuid not null references public.rental_listings(id),
 applicant_id uuid not null references auth.users(id), full_name text not null check(length(full_name) between 2 and 120),
 email text not null check(length(email)<=250), phone text not null check(length(phone) between 7 and 30),
 message text not null check(length(message) between 1 and 2000),
 status text not null default 'submitted' check(status in ('submitted','reviewing','approved','declined')),
 created_at timestamptz not null default now(), unique(listing_id,applicant_id)
);
create table if not exists public.rental_messages (
 id uuid primary key default gen_random_uuid(), application_id uuid not null references public.rental_applications(id),
 sender_id uuid not null references auth.users(id), body text not null check(length(body) between 1 and 2000),
 created_at timestamptz not null default now()
);
create index if not exists rental_listings_public_idx on public.rental_listings(status,created_at desc);
create index if not exists rental_applications_listing_idx on public.rental_applications(listing_id);
create index if not exists rental_messages_application_idx on public.rental_messages(application_id,created_at);
alter table public.rental_listings enable row level security;
alter table public.rental_applications enable row level security;
alter table public.rental_messages enable row level security;
-- Owners may read their drafts. Published listings are readable by anyone.
create policy "public listings or own drafts" on public.rental_listings for select using(status='published' or owner_id=(select auth.uid()));
create policy "owner submits pending listing" on public.rental_listings for insert to authenticated with check(owner_id=(select auth.uid()) and status='pending');
-- No client updates to listings. Staff publishes using the server-side dashboard/service role.
create policy "participants read applications" on public.rental_applications for select to authenticated using(applicant_id=(select auth.uid()) or exists(select 1 from public.rental_listings l where l.id=listing_id and l.owner_id=(select auth.uid())));
create policy "tenant applies to published home" on public.rental_applications for insert to authenticated with check(applicant_id=(select auth.uid()) and status='submitted' and exists(select 1 from public.rental_listings l where l.id=listing_id and l.status='published' and l.owner_id<>(select auth.uid())));
create policy "owner updates application" on public.rental_applications for update to authenticated using(exists(select 1 from public.rental_listings l where l.id=listing_id and l.owner_id=(select auth.uid()))) with check(exists(select 1 from public.rental_listings l where l.id=listing_id and l.owner_id=(select auth.uid())));
create policy "participants read messages" on public.rental_messages for select to authenticated using(exists(select 1 from public.rental_applications a join public.rental_listings l on l.id=a.listing_id where a.id=application_id and (a.applicant_id=(select auth.uid()) or l.owner_id=(select auth.uid()))));
create policy "participants send messages" on public.rental_messages for insert to authenticated with check(sender_id=(select auth.uid()) and exists(select 1 from public.rental_applications a join public.rental_listings l on l.id=a.listing_id where a.id=application_id and (a.applicant_id=(select auth.uid()) or l.owner_id=(select auth.uid()))));
revoke all on public.rental_listings,public.rental_applications,public.rental_messages from anon,authenticated;
grant select on public.rental_listings to anon,authenticated;
grant insert on public.rental_listings to authenticated;
grant select,insert on public.rental_applications to authenticated;
grant update(status) on public.rental_applications to authenticated;
grant select,insert on public.rental_messages to authenticated;
