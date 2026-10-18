"""
AI Tech Consultant - Knowledge Brain
Seed Knowledge Base Articles for Brilliant Directories Support.
Provides realistic, high-fidelity help center articles pre-indexed into ChromaDB and SQLite.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
import hashlib

from app.database import Database
from app.models import ArticleContent, ArticleImage, PageRecord, PageStatus
from app.vector_store import VectorStore
from ingestion.chunker import ArticleChunker

logger = logging.getLogger(__name__)

SEED_ARTICLES_DATA = [
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000078901-pointing-domain",
        "title": "How to Point Your Domain Name to Brilliant Directories",
        "category": "Domain Settings & DNS Management",
        "folder": "Domain Setup",
        "headings": [
            "Overview",
            "Step 1: Configure A-Record at Your Registrar",
            "Step 2: Add CNAME Record for WWW Subdomain",
            "Step 3: Update Primary Website Domain in BD Admin",
            "Step 4: Enable Automated SSL Certificate",
            "Troubleshooting DNS Propagation & 404 Errors"
        ],
        "content_text": """# How to Point Your Domain Name to Brilliant Directories

## Overview
Pointing your custom domain name (e.g., yourdirectory.com) to your Brilliant Directories website allows visitors and search engines to access your platform using your branded web address rather than the default staging URL. Brilliant Directories provides dedicated high-availability hosting with automated SSL encryption.

## Step 1: Configure A-Record at Your Registrar
Log in to your domain registrar account (e.g., GoDaddy, Namecheap, Cloudflare, Google Domains, Bluehost) and access your DNS Management / Advanced DNS settings.
1. Locate the existing A-Record with Host '@' (or root).
2. Edit or create the A-Record pointing to Brilliant Directories Server IP: 54.208.192.173.
3. Set the TTL (Time to Live) to 300 seconds (or 1/2 hour) for faster propagation.
Note: If using Cloudflare, ensure the proxy status is set to 'DNS Only' (grey cloud) during initial SSL provisioning.

## Step 2: Add CNAME Record for WWW Subdomain
To ensure visitors typing 'www.yourdirectory.com' are seamlessly directed to your website:
1. Locate or create a CNAME record.
2. Set the Host / Name to 'www'.
3. Set the Value / Target to '@' or your root domain 'yourdirectory.com'.

## Step 3: Update Primary Website Domain in BD Admin
Once DNS records are configured:
1. Log in to your Brilliant Directories Admin Dashboard.
2. Navigate to Settings > Domain Manager.
3. In the 'Primary Website Domain' field, enter your clean domain name without 'http://' or 'www' (e.g., yourdirectory.com).
4. Click 'Save Changes'.
5. Flush system caches by navigating to Developer Hub > Clear Cache.

## Step 4: Enable Automated SSL Certificate
Brilliant Directories provides free, automated Let's Encrypt SSL certificates.
1. After saving your domain, click 'Install Free SSL Certificate' in Settings > Domain Manager.
2. The platform will automatically verify that the A-Record points to 54.208.192.173.
3. Once validated, your HTTPS padlock will activate across all member checkout and login pages within 15 minutes.

## Troubleshooting DNS Propagation & 404 Errors
- Global DNS propagation typically takes between 15 minutes and 24 hours. Use tools like Whatsmydns.net to check propagation of 54.208.192.173 worldwide.
- If you see a 'Website Not Found' error, confirm that there are no conflicting AAAA (IPv6) records at your registrar, as IPv6 must be removed.
- Always clear your local browser cache or test in an Incognito / Private window.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/dns_a_record_setup.png",
                "alt_text": "DNS A-Record setup pointing to IP 54.208.192.173",
                "context_text": "Edit or create the A-Record pointing to Brilliant Directories Server IP: 54.208.192.173."
            },
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/domain_manager_admin.png",
                "alt_text": "Brilliant Directories Domain Manager settings panel",
                "context_text": "Navigate to Settings > Domain Manager and enter your primary website domain."
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000045612-stripe-setup",
        "title": "Connecting Stripe Payment Gateway & Troubleshooting Checkout",
        "category": "Finance & Billing",
        "folder": "Payment Gateways",
        "headings": [
            "Overview",
            "Step 1: Obtain Your Stripe API Credentials",
            "Step 2: Paste Keys into Brilliant Directories Gateway Settings",
            "Step 3: Register Stripe Webhook Endpoint",
            "Step 4: Enable Test Mode vs Live Mode",
            "Troubleshooting Mobile Checkout & 3D-Secure Failures"
        ],
        "content_text": """# Connecting Stripe Payment Gateway & Troubleshooting Checkout

## Overview
Stripe is the premier recommended payment gateway for Brilliant Directories, enabling recurring member subscriptions, paid lead purchases, digital product sales, and automated credit card retries across 135+ currencies with full SCA (Strong Customer Authentication) 3D-Secure 2 compliance.

## Step 1: Obtain Your Stripe API Credentials
1. Log in to your Stripe Dashboard at dashboard.stripe.com.
2. Ensure you are viewing your Live account (toggle off Test Mode in top right).
3. Navigate to Developers > API Keys.
4. Copy your 'Publishable key' (starts with pk_live_...).
5. Click 'Reveal live key' to copy your 'Secret key' (starts with sk_live_...). Keep this confidential.

## Step 2: Paste Keys into Brilliant Directories Gateway Settings
1. In your Brilliant Directories admin portal, navigate to Finance > Payment Gateways.
2. From the Gateway dropdown, select 'Stripe'.
3. Paste your Publishable Key into the 'Stripe Publishable Key' field.
4. Paste your Secret Key into the 'Stripe Secret Key' field.
5. Select your default transaction currency (e.g., USD, CAD, EUR, GBP, AUD).
6. Click 'Save Gateway Settings'.

## Step 3: Register Stripe Webhook Endpoint
Webhooks inform Brilliant Directories when recurring monthly or annual subscription payments succeed or fail in Stripe.
1. In Stripe Dashboard, navigate to Developers > Webhooks > Add Destination.
2. Enter your endpoint URL: https://yourdirectory.com/api/stripe/webhook
3. Select events to listen to:
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
4. Copy the Webhook Signing Secret (starts with whsec_...) into BD Finance > Payment Gateways.

## Step 4: Enable Test Mode vs Live Mode
Before launching, you can test signups without real money:
- Toggle 'Sandbox / Test Mode' to YES in BD Payment Gateways.
- Enter your Stripe test keys (pk_test_... and sk_test_...).
- Use Stripe test card 4242 4242 4242 4242 with any future expiration date and CVC.
- Switch to Live mode once you have confirmed successful invoice generation.

## Troubleshooting Mobile Checkout & 3D-Secure Failures
- Error: 'Card Declined / Authentication Required': This indicates an EU or UK bank requiring Two-Factor Authentication via 3DS. Ensure you have enabled the Brilliant Directories Stripe 3DS SCA Add-on.
- Error: 'Mobile keyboard blocks submit button': Ensure your checkout layout uses standard Bootstrap forms and that custom JavaScript modals are not trapping the focus event.
- For recurring subscription status discrepancies, check the Webhooks log in your Stripe Dashboard for 200 OK responses.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/stripe_api_keys.png",
                "alt_text": "Stripe API Key configuration in BD Finance settings",
                "context_text": "Paste your Publishable Key and Secret Key into the Stripe Gateway settings."
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000034567-csv-member-import",
        "title": "How to Bulk Import Members via CSV Without Geocoding Errors",
        "category": "Member Management",
        "folder": "Data Import & Export",
        "headings": [
            "Overview",
            "Step 1: Prepare Your CSV File & Header Formatting",
            "Step 2: Map Custom Fields & Membership Plans",
            "Step 3: Geocoding Coordinates & Address Requirements",
            "Step 4: Executing the Upload & Handling Batch Limits",
            "Post-Import: Password Setting & Automated Welcome Emails"
        ],
        "content_text": """# How to Bulk Import Members via CSV Without Geocoding Errors

## Overview
Brilliant Directories allows administrators to import thousands of existing business listings or professional members using CSV (Comma Separated Values) files. Properly formatting your CSV ensures flawless address geocoding, automated directory categorization, and zero duplicate account creation.

## Step 1: Prepare Your CSV File & Header Formatting
Save your spreadsheet strictly as CSV UTF-8 format. The recommended standard headers include:
- email (Unique identifier; required)
- first_name, last_name, company
- phone_number, website
- address1, city, state_code (2-letter ISO, e.g. CA, NY, TX), zip_code, country_code (US, CA, UK, etc.)
- profession / top_category (must match your Directory Top Level Category exactly)
- sub_categories (comma or semicolon separated list)

## Step 2: Map Custom Fields & Membership Plans
1. Navigate to My Members > Import Members.
2. Select the destination Membership Plan (e.g., 'Verified Contractor', 'Featured Doctor', 'Free Listing').
3. Choose whether imported members should be set to 'Active', 'Pending Approval', or 'Claim Listing'.
4. Upload your CSV file and click 'Continue to Column Mapping'.
5. Map each CSV column to the corresponding BD Member Profile database field.

## Step 3: Geocoding Coordinates & Address Requirements
To enable visitors to find members via radius / postal code searches, listings must be geocoded:
- If your CSV includes latitude ('lat') and longitude ('lon') columns, map them directly. This bypasses API rate limits and is 100% accurate.
- If your CSV lacks coordinates, BD will query the Google Maps Geocoding API. Ensure each record has at minimum city, state, and zip code to prevent ambiguous coordinates.

## Step 4: Executing the Upload & Handling Batch Limits
- For optimal server performance and memory stability, limit CSV files to 5,000 members per batch.
- If you have 25,000 listings, split them into five files (Part1.csv, Part2.csv, etc.).
- The import progress bar updates in real time. Do not close or refresh the browser tab until the completion report appears.

## Post-Import: Password Setting & Automated Welcome Emails
- Imported members are generated with secure randomized password hashes.
- To invite imported members to claim or manage their profile:
  1. Go to Emails > Send Newsletter.
  2. Filter recipient list by Import Date or Membership Plan.
  3. Use the 'Claim Your Profile / Password Reset' template containing the dynamic %%%password_reset_link%%% variable.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/csv_column_mapping.png",
                "alt_text": "CSV Column Mapping interface in Member Import tool",
                "context_text": "Map each CSV column to the corresponding BD Member Profile database field."
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000055432-custom-widgets",
        "title": "Developer Hub: Creating Custom Widgets & Overriding System Code",
        "category": "Custom Code & Widgets",
        "folder": "Developer Hub",
        "headings": [
            "Overview",
            "Step 1: Accessing the Widget Manager",
            "Step 2: Creating a New Custom Widget",
            "Step 3: Embedding Widgets with Shortcodes",
            "Step 4: Overriding Core System Widgets Safely",
            "PHP & JavaScript Execution Rules & Developer Best Practices"
        ],
        "content_text": """# Developer Hub: Creating Custom Widgets & Overriding System Code

## Overview
The Brilliant Directories Developer Hub gives software engineers and web consultants full freedom to inject custom HTML, PHP, JavaScript, and CSS into any part of the platform. Using custom widgets ensures your custom code is preserved across official platform software updates.

## Step 1: Accessing the Widget Manager
1. Log in to your Admin Dashboard as an Administrator.
2. In the left navigation menu, expand 'Developer Hub'.
3. Click 'Widget Manager'.
4. Here you can search through hundreds of default core widgets or manage your custom implementations.

## Step 2: Creating a New Custom Widget
1. In Widget Manager, click the green 'New Widget' button in the top right.
2. Enter a unique, lowercase Widget Code Name (e.g., 'custom_doctor_bio_card' or 'contractor_lead_form').
3. Write your code in the built-in IDE editor:
   - PHP and HTML in the main code tab.
   - CSS in the Custom CSS tab (automatically minified into site stylesheet).
   - JavaScript in the Custom JS tab (automatically placed before closing </body> tag).
4. Click 'Save Changes'.

## Step 3: Embedding Widgets with Shortcodes
You can embed your custom widget anywhere in the platform:
- In Static Pages or Blog Posts via the WYSIWYG editor using the shortcode: [widget=custom_doctor_bio_card]
- Inside other custom widgets or layout templates using PHP:
  echo widget('custom_doctor_bio_card', '', $wa);
- Inside Header, Footer, or Sidebar layouts via the Design Settings > Layout blocks.

## Step 4: Overriding Core System Widgets Safely
If you need to customize default platform behavior (e.g., the search bar or member profile header):
1. In Widget Manager, locate the core widget (e.g., 'Bootstrap Theme - Header - Right').
2. Click 'Customize'.
3. This creates a safe copy in your Custom Widgets list.
4. Edit the copy as needed. The Brilliant Directories compiler prioritizes custom widgets over system widgets.
5. If you ever want to revert, click 'Disable' or 'Delete Customization' to instantly restore the factory original.

## PHP & JavaScript Execution Rules & Developer Best Practices
- Never use 'die()' or 'exit()' inside widgets, as this halts execution of the entire page render pipeline.
- Access member profile variables via the global array '$user' and website settings via '$wa'.
- Always test JavaScript in Developer Tools (F12) console to avoid uncaught script exceptions that could prevent other widgets from rendering.
- After saving any widget code changes, flush the server template cache via Developer Tools > Clear Cache.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/widget_manager_editor.png",
                "alt_text": "Brilliant Directories Widget Manager code editor",
                "context_text": "Enter your custom PHP, HTML, CSS, and JS inside the Widget Manager editor."
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000067890-smtp-deliverability",
        "title": "How to Configure Custom SMTP & Prevent Spam Delivery",
        "category": "Email & Notifications",
        "folder": "Email Deliverability",
        "headings": [
            "Overview",
            "Step 1: Set Up an External SMTP Provider",
            "Step 2: Enter SMTP Credentials in Brilliant Directories",
            "Step 3: Configure SPF and DKIM DNS Records",
            "Step 4: Send Test Notification Message",
            "Troubleshooting Spam Filtering & DMARC Alignment"
        ],
        "content_text": """# How to Configure Custom SMTP & Prevent Spam Delivery

## Overview
High email deliverability is critical for directory websites sending member welcome emails, lead notifications, invoice receipts, and password reset requests. While Brilliant Directories includes shared default transactional servers, connecting a dedicated SMTP provider (e.g., SendGrid, Mailgun, Amazon SES, Postmark) guarantees 99%+ inbox placement and protects your domain sender reputation.

## Step 1: Set Up an External SMTP Provider
1. Create an account with a reputable email infrastructure provider (SendGrid, Mailgun, or Amazon SES).
2. Complete sender domain authentication inside your SMTP provider dashboard.
3. Generate an API Key or SMTP Username and Password with 'Mail.Send' permissions.

## Step 2: Enter SMTP Credentials in Brilliant Directories
1. In your Brilliant Directories Admin, navigate to Settings > Email Settings.
2. Locate the 'Sending Method' option and select 'Custom SMTP Server'.
3. Fill in the connection parameters:
   - SMTP Host: (e.g., smtp.sendgrid.net or smtp.mailgun.org)
   - SMTP Port: 587 (Recommended TLS) or 465 (SSL)
   - SMTP Username: (e.g., apikey for SendGrid)
   - SMTP Password: Your generated API key secret
   - Encryption: TLS
4. Set your 'Default From Email' to an email address sharing your custom domain (e.g., notifications@yourdirectory.com).
5. Click 'Save Email Settings'.

## Step 3: Configure SPF and DKIM DNS Records
At your domain registrar's DNS settings, add the required sender authorization records:
- SPF Record (TXT):
  Host: @
  Value: v=spf1 include:sendgrid.net ~all
- DKIM Records (CNAME):
  Add the 2 or 3 CNAME records generated by your SMTP provider to cryptographically sign every outgoing email.
- DMARC Policy (TXT):
  Host: _dmarc
  Value: v=DMARC1; p=none; rua=mailto:dmarc@yourdirectory.com

## Step 4: Send Test Notification Message
1. In BD Settings > Email Settings, scroll to the 'Test Email Configuration' tool.
2. Enter your personal recipient email address.
3. Click 'Send Test Email'.
4. Confirm receipt and verify that email headers display 'SPF: PASS' and 'DKIM: PASS'.

## Troubleshooting Spam Filtering & DMARC Alignment
- Never use free webmail addresses (e.g., @gmail.com or @yahoo.com) as your 'Default From Email', as modern DMARC policies will reject or mark these messages as phishing.
- Ensure all automated email templates (Emails > Email Templates) maintain a balanced text-to-link ratio and avoid aggressive spam keywords like 'FREE MONEY' or all-caps subject lines.
- Monitor bounce and spam complaint rates inside your SMTP dashboard; maintain complaints below 0.1%.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/smtp_settings_bd.png",
                "alt_text": "Custom SMTP configuration in Email Settings",
                "context_text": "Configure SMTP host, port 587, and API credentials in Settings > Email Settings."
            }
        ]
    },
    {
        "url": "https://support.brilliantdirectories.com/support/solutions/articles/12000089123-lead-distribution",
        "title": "Lead Distribution Automation & Pay-Per-Lead Credit Rules",
        "category": "Leads & Inquiries",
        "folder": "Lead Management",
        "headings": [
            "Overview",
            "Step 1: Configure Auto-Match Search Radius",
            "Step 2: Set Pricing & Credit Deductions per Lead Category",
            "Step 3: Automated Member SMS & Email Notifications",
            "Step 4: Lead Acceptance & Claim Expiration Timeframes",
            "Troubleshooting Unmatched Inquiries & Lead Refunds"
        ],
        "content_text": """# Lead Distribution Automation & Pay-Per-Lead Credit Rules

## Overview
Monetizing member leads is one of the highest revenue-generating business models on the Brilliant Directories platform. The automated Lead Distribution System matches consumer quote inquiries with qualified directory members based on geographical proximity, service categories, and subscription tier rules.

## Step 1: Configure Auto-Match Search Radius
1. Navigate to Leads > Lead Settings.
2. Set the default matching radius (e.g., 25 miles or 40 km from consumer postal code).
3. Select the matching criteria:
   - Match by Top Category and Sub-Categories.
   - Match by Location (Exact City vs Radius from Zip/Postal code).
4. Configure maximum matched members per lead (e.g., send lead to up to 3 contractors or doctors).

## Step 2: Set Pricing & Credit Deductions per Lead Category
1. In Finance > Membership Plans, edit the target plan (e.g., 'Pro Contractor').
2. Navigate to the 'Leads' tab.
3. Choose the lead acquisition model:
   - Free / Included with monthly subscription.
   - Pay-Per-Lead: Set fixed price (e.g., $25 per accepted lead) or credit deduction (e.g., 5 credits).
4. If using credit packages, members can purchase credit bundles in their member dashboard via Stripe.

## Step 3: Automated Member SMS & Email Notifications
When a consumer submits a lead request form:
- The system automatically triggers an email preview with masked consumer contact info to matched members.
- If the Twilio SMS Add-on is active, an instant SMS text alert is dispatched: 'New Lead in your area: Kitchen Remodeling. Click here to preview and accept.'

## Step 4: Lead Acceptance & Claim Expiration Timeframes
- Set the 'Acceptance Expiration Window' (e.g., 48 hours).
- The first members to click 'Accept & Purchase Lead' receive the unmasked consumer contact details (full name, phone, address, and project notes).
- Once the maximum allowed members have purchased the lead, it automatically locks to prevent market saturation.

## Troubleshooting Unmatched Inquiries & Lead Refunds
- If a lead status is 'Pending / Unmatched', check if any active members exist within the requested geographical radius and category. You can manually re-assign the lead to any member in Leads > Manage Leads.
- Admins can issue instant credit or card refunds with one click in Leads > Manage Leads if a customer provided an invalid phone number.""",
        "images": [
            {
                "image_url": "https://cdn.brilliantdirectories.com/attachments/lead_settings_preview.png",
                "alt_text": "Lead distribution settings and match radius controls",
                "context_text": "Configure auto-match radius and lead pricing in Leads > Lead Settings."
            }
        ]
    }
]


async def seed_knowledge_base(db: Database, vector_store: VectorStore) -> dict:
    """Ingest seed articles into SQLite and ChromaDB vector store."""
    chunker = ArticleChunker(chunk_size=400, chunk_overlap=60)
    now_iso = datetime.now(timezone.utc).isoformat()

    indexed_articles = 0
    total_chunks_added = 0

    for item in SEED_ARTICLES_DATA:
        url = item["url"]
        content_text = item["content_text"]
        content_hash = hashlib.md5(content_text.encode("utf-8")).hexdigest()

        # 1. Save or update Page in SQLite
        await db.upsert_page(url, last_modified=now_iso)
        await db.update_page_status(
            url=url,
            status=PageStatus.INDEXED,
            content_hash=content_hash,
            title=item["title"],
        )

        # 2. Save Article Images in SQLite
        images = []
        for idx, img in enumerate(item.get("images", [])):
            art_img = ArticleImage(
                article_url=url,
                image_url=img["image_url"],
                alt_text=img.get("alt_text", ""),
                context_text=img.get("context_text", ""),
                description=img.get("alt_text", ""),
                position_index=idx,
                processed=True,
            )
            await db.upsert_image(art_img)
            await db.update_image_description(url, img["image_url"], img.get("alt_text", ""))
            images.append(art_img)

        # 3. Chunk article content
        article_content = ArticleContent(
            url=url,
            title=item["title"],
            category=item.get("category"),
            folder=item.get("folder"),
            content_text=content_text,
            headings=item.get("headings", []),
            images=images,
            content_hash=content_hash,
            word_count=len(content_text.split()),
            parsed_at=datetime.now(timezone.utc),
        )

        chunks = chunker.chunk_article(article_content)

        # 4. Store chunks in ChromaDB
        added = await vector_store.add_chunks(chunks)
        total_chunks_added += added
        indexed_articles += 1

    logger.info(f"Knowledge Brain seeded successfully: {indexed_articles} articles, {total_chunks_added} chunks.")
    return {
        "articles_seeded": indexed_articles,
        "chunks_indexed": total_chunks_added,
    }
