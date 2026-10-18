"""
AI Tech Consultant - Meeting to Scope
Realistic client discovery meeting transcripts for Brilliant Directories consulting projects.
"""

SEED_MEETINGS = [
  {
    "metadata": {
      "id": "MEET-2001",
      "title": "MedMatch Pro – National Healthcare Directory Scoping Session",
      "client_name": "Dr. Julian Vance",
      "client_company": "MedMatch Healthcare Group",
      "client_email": "julian.vance@medmatchpro.org",
      "date": "2026-03-12",
      "duration_minutes": 52,
      "participants": [
        "Dr. Julian Vance (CEO, MedMatch)",
        "Claire Dubois (Operations Director)",
        "Jordan Lee (Lead AI Tech Consultant)"
      ]
    },
    "transcript": """[00:00] Jordan Lee: Welcome everyone! Dr. Vance and Claire, great to connect today. The objective of this discovery call is to review your vision for MedMatch Pro, map out your technical and functional requirements, and establish a clear Scope of Work for building this on the Brilliant Directories platform. Let's start with your high-level business model.

[00:45] Dr. Julian Vance: Thanks Jordan. In short, MedMatch Pro will be a nationwide directory connecting patients with verified medical specialists—initially cardiologists, dermatologists, orthopedic surgeons, and pediatricians across 10 major metropolitan areas. We have an initial database of roughly 12,000 pre-vetted physicians.

[02:10] Claire Dubois: From a monetization perspective, we plan three membership tiers: 
1. Basic Profile (Free claimable listing with clinic address and phone).
2. Verified Specialist ($59/month or $590/year) which unlocks patient review management, direct appointment inquiry forms, and our 'Board Certified & Verified' badge.
3. Multi-Provider Clinic/Practice Network ($299/month) which permits managing up to 8 physician sub-accounts under a central billing invoice.

[04:20] Jordan Lee: Excellent structure. Brilliant Directories natively supports hierarchical membership plans with recurring subscription billing via Stripe. For the Clinic tier managing multiple practitioners, we can configure the BD Multi-Listing / Sub-Accounts Add-on so the clinic administrator can invite doctors while keeping consolidated billing.

[05:55] Dr. Julian Vance: That sounds ideal. Now, regarding search: patients need to search by medical specialty, accepted health insurance carriers (like Aetna, BlueCross, Medicare), and distance radius from their ZIP code. Can BD handle filtering doctors who specifically take Medicare within 15 miles?

[07:15] Jordan Lee: Yes! Brilliant Directories has built-in Google Maps geocoding and radial distance search. We will set up custom multi-level category dropdowns for Specialties, Sub-specialties, and an Insurances Accepted custom checkbox field on the doctor's profile.

[09:00] Claire Dubois: What about the appointment inquiry form? When a patient visits Dr. Smith's profile, they should be able to submit an inquiry requesting an appointment. But we must ensure the form includes a disclaimer that it's for non-emergency scheduling and sends an instant email and SMS alert to the doctor's office.

[10:45] Jordan Lee: Absolutely. We will customize the member contact form widget with the medical disclaimer checkbox and hook it into SendGrid for verified SPF/DKIM delivery. For SMS alerts, we can set up a webhook to Twilio so the clinic receptionist receives an SMS ping whenever a consultation request is submitted.

[12:30] Dr. Julian Vance: Regarding our existing database: we have an Excel/CSV spreadsheet with the 12,000 doctors, NPI numbers, addresses, and specialties. Can you handle importing all of them and geocoding their coordinates?

[14:00] Jordan Lee: Yes. We will normalize the CSV headers to match BD schema, run postal geocoding, and batch-import them in segments of 2,000 records to prevent server timeouts. All 12,000 will be set as 'Claimable Listings'. When a doctor visits, they can click 'Claim Your Profile', verify their NPI number and medical license, and upgrade to the paid tier.

[16:20] Claire Dubois: That 'Claim Listing' flow is critical. How does the verification work? Can we hold upgraded claims in an admin moderation queue before the badge goes live?

[17:40] Jordan Lee: Exactly. We will configure BD's Claim Listings Add-on with admin approval enabled. When a doctor claims their listing and completes Stripe checkout, their status changes to 'Pending Verification'. Your team reviews their license PDF upload in the BD Admin, clicks 'Approve', and the Verified Badge and priority search ranking activate automatically.

[19:15] Dr. Julian Vance: What is out of scope for Phase 1? We don't want to get bogged down in custom telemedicine video calls or full EHR electronic health record syncing right now.

[20:30] Jordan Lee: That is a very smart boundary. Telemedicine video rooms and bidirectional Epic/Cerner EHR integrations are definitely out of scope for Phase 1. Patients will simply submit appointment requests, and the doctor's office confirms via phone or their own portal.

[22:00] Claire Dubois: What is the estimated timeline and budget for a project like this? We are aiming to launch within 6 to 8 weeks.

[23:15] Jordan Lee: An 6 to 8-week timeline is realistic. We will break this into 4 structured phases:
- Phase 1: Core BD Platform Setup, Custom Domain & Branding Theme (Weeks 1-2)
- Phase 2: Category Architecture, Custom Fields & Stripe Gateways (Weeks 3-4)
- Phase 3: Data Migration of 12,000 Doctors & Claim Listing Workflows (Weeks 5-6)
- Phase 4: Twilio Webhook Integration, QA Testing & Launch (Weeks 7-8)

Estimated effort is approximately 68 consulting hours. I will generate the complete Scope of Work document with all phase deliverables, milestone payment schedule, and add-on recommendations for you to review!

[25:00] Dr. Julian Vance: Fantastic, Jordan. Looking forward to reviewing the formal SOW.""",
    "custom_notes": "Client has strong existing medical database. Prioritize Claim Listing workflow and geocoded insurance filters. Standardize on native BD add-ons wherever feasible."
  },
  {
    "metadata": {
      "id": "MEET-2002",
      "title": "HomeService Hub – Contractor Directory & Lead Distribution Scoping",
      "client_name": "Marcus Thorne",
      "client_company": "Thorne Ventures",
      "client_email": "marcus@thorneventures.com",
      "date": "2026-03-08",
      "duration_minutes": 48,
      "participants": [
        "Marcus Thorne (Managing Partner)",
        "Derek Walsh (Technical Project Lead)",
        "Jordan Lee (Lead AI Tech Consultant)"
      ]
    },
    "transcript": """[00:00] Jordan Lee: Hello Marcus and Derek. Today we're diving into the technical scoping for HomeService Hub. Marcus, tell us about the legacy setup you're replacing.

[00:40] Marcus Thorne: We currently run an aging WordPress directory with roughly 7,500 home service contractors—plumbers, roofers, electricians, HVAC pros across Texas and Florida. The site has slowed to a crawl, database queries timeout, and the lead generation system breaks constantly. We decided to migrate entirely to Brilliant Directories.

[02:15] Derek Walsh: Our primary requirement is automated lead matching. When a homeowner fills out a 'Get 3 Free Estimates' form—say, for emergency AC repair in Austin—the system must automatically match the request to the 3 highest-rated contractors within a 25-mile radius and broadcast the lead.

[04:00] Jordan Lee: Brilliant Directories features a dedicated Automated Lead Routing engine. When the homeowner submits the quote request, BD evaluates the trade category and location radius, deducts lead purchase credits from the matched contractors' prepaid balance, and dispatches the lead notification.

[05:40] Marcus Thorne: What about contractor pricing? Contractors will subscribe for $99/month for profile visibility, but leads should cost $25 to $45 each depending on the project value.

[07:10] Jordan Lee: That is BD's sweet spot. We configure recurring subscriptions for base membership, combined with the Pay-Per-Lead Credit System. Contractors can buy a $200 lead credit pack through Stripe, and credits auto-deduct when they accept a dispatched quote.

[09:00] Derek Walsh: We also need custom review collection. After a job is completed, can we trigger an automated review request email to the homeowner?

[10:30] Jordan Lee: Yes, through the BD Member Reviews Add-on and custom email notification templates. We will configure Star Ratings with criteria like Punctuality, Quality, and Value.

[12:15] Marcus Thorne: What about data migration from our existing WordPress database? We have contractor profile data, business licenses, logos, and past reviews.

[13:40] Jordan Lee: We will export your WordPress wp_posts and custom post meta into CSV format, clean and map the fields, migrate high-resolution contractor logos into BD media storage, and re-import into the new database with zero downtime.

[15:20] Derek Walsh: What about SMS notifications? Most roofers don't check email on the job site; they need an instant text message with a one-click button to accept the lead.

[17:00] Jordan Lee: We will implement a custom webhook connecting BD's lead creation trigger to Zapier / Twilio SMS. When a homeowner clicks submit, contractors receive a text: 'New Roof Repair Lead in 78701. Tap to accept.'

[19:00] Marcus Thorne: What is the total effort and milestone timeline for migrating the data and launching the lead engine?

[20:15] Jordan Lee: Total effort is estimated around 84 consulting hours across 4 phases:
- Phase 1: BD Architecture & Custom Austin/Texas Regional Themes (Weeks 1-2)
- Phase 2: WordPress Data Extraction, Cleansing & Migration of 7,500 Contractors (Weeks 3-4)
- Phase 3: Lead Distribution Engine & Pay-Per-Lead Stripe Billing (Weeks 5-7)
- Phase 4: Twilio SMS Webhook, End-to-End Lead Simulation & DNS Cutover (Weeks 8-9)

I will document this in a detailed Scope of Work with milestone deliverables and fee schedules.

[22:00] Marcus Thorne: Let's do it Jordan. Please send over the SOW.""",
    "custom_notes": "WordPress data migration requires careful slug mapping for SEO preservation. Pay-per-lead system is the client's core revenue driver."
  },
  {
    "metadata": {
      "id": "MEET-2003",
      "title": "ArtisanGuild – Indie Crafts & Makers Directory Discovery",
      "client_name": "Elena Chen",
      "client_company": "ArtisanGuild Collective",
      "client_email": "elena@artisanguild.com",
      "date": "2026-03-15",
      "duration_minutes": 38,
      "participants": [
        "Elena Chen (Founder, ArtisanGuild)",
        "Jordan Lee (Lead AI Tech Consultant)"
      ]
    },
    "transcript": """[00:00] Jordan Lee: Hi Elena! Excited to discuss ArtisanGuild today. Tell me about the artisans you're featuring.

[00:35] Elena Chen: ArtisanGuild is an online directory and showcase for 3,500 independent potters, woodworkers, jewelry makers, and textile artists. Our members want a beautiful portfolio page with photo galleries of their handmade items, links to their Etsy or Shopify shops, and a contact form for custom bespoke commissions.

[02:10] Jordan Lee: That fits Brilliant Directories wonderfully. With the Photo Albums & Community Articles add-ons, makers can upload high-resolution image galleries, tag their products, and showcase custom commission options.

[03:40] Elena Chen: We also want a featured Artisan of the Week slider on the home page and an interactive map showing artisan studios open for weekend studio tours.

[05:00] Jordan Lee: Brilliant Directories includes a Featured Member Carousel widget that we can embed on your homepage, and the Google Maps studio tour view can filter makers with physical studio hours.

[06:30] Elena Chen: What's the timeline and budget? We have a tight budget around $6,000 to $7,500 and want to launch in about 4 to 5 weeks.

[07:45] Jordan Lee: That budget aligns well with an agile 46-hour scope by leveraging native Brilliant Directories widgets with minimal custom coding:
- Phase 1: Warm Artisan Theme & Responsive Layouts (Weeks 1-2)
- Phase 2: Category Taxonomy & Maker Portfolios with Etsy Links (Weeks 2-3)
- Phase 3: Studio Tour Maps, Member Ingestion & Launch (Weeks 4-5)

[09:30] Elena Chen: Perfect. Looking forward to the proposal!""",
    "custom_notes": "Visually focused project. Heavy use of image galleries and clean modern typography. Fast 4-5 week delivery window."
  }
]
