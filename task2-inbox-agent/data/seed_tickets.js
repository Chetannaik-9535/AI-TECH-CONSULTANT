/**
 * Seed tickets representing real-world Brilliant Directories support inquiries.
 */
export const SEED_TICKETS = [
  {
    id: "TICK-1001",
    customer: {
      name: "Marcus Vance",
      email: "marcus@directoryplus.org",
      company: "DirectoryPlus Network",
      tier: "VIP Enterprise",
      plan: "Annual Enterprise BD",
      siteUrl: "https://directoryplus.org",
      avatar: "MV"
    },
    subject: "Members getting 404 error after custom domain change",
    message: "We pointed our new domain directoryplus.org via A Record yesterday. The home page loads fine, but when clicking on member profile URLs or the login link, users are greeted with a 404 page not found error. How do we update the primary directory URL settings in the BD admin panel to regenerate the permalinks?",
    category: "Domains & SSL",
    priority: "High",
    status: "needs_review", // unassigned, needs_review, auto_drafted, escalated, resolved
    sentiment: "Frustrated",
    urgencyScore: 84,
    createdAt: new Date(Date.now() - 32 * 60 * 1000).toISOString(),
    aiAnalysis: {
      detectedIssue: "Domain change permalink desynchronization",
      requiredAction: "Update Website Domain setting in Admin > Settings > Domain Manager & clear system cache",
      confidence: 0.94,
      escalationRecommended: false,
      recommendedTone: "Empathetic, step-by-step guidance"
    },
    retrievedSources: [
      {
        title: "How to Point Your Domain Name to Brilliant Directories",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000078901-pointing-domain",
        section: "Step 3: Update Default Website Domain in Admin",
        relevanceScore: 0.96,
        snippet: "After updating DNS A-Records, navigate to Settings > Domain Manager in your admin portal. Ensure the primary URL matches your live domain and save to refresh .htaccess rewrites."
      },
      {
        title: "Resolving 404 Errors on Search Results & Member Profile Pages",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000034567-404-member-profiles",
        section: "Flushing BD Cache",
        relevanceScore: 0.91,
        snippet: "Go to Dashboard > Developer Tools > Clear Cache. This flushes stored routing tables and rebuilds directory permalinks."
      }
    ],
    draftReply: {
      subject: "Re: Members getting 404 error after custom domain change [TICK-1001]",
      body: `Hi Marcus,

Thank you for contacting technical support. We understand how critical it is for member profile URLs and login pages to resolve seamlessly after a domain launch.

This 404 issue typically occurs because the directory's internal routing tables still reflect the temporary staging URL. You can resolve this in 2 quick steps:

1. **Verify Default Domain in Admin:**
   - Log into your Brilliant Directories Admin Panel.
   - Go to **Settings > Domain Manager**.
   - Ensure the **Primary Website Domain** is explicitly set to \`https://directoryplus.org\` (with your preferred SSL protocol).
   - Click **Save Changes**.

2. **Refresh System Permalinks & Flush Cache:**
   - On the top admin toolbar, click the **Refresh Live Website** button (or navigate to **Developer Hub > Clear System Cache**).
   - This re-indexes all member profile slugs against your new domain.

For detailed screenshots of the Domain Manager screen, refer to our official guide:
• [How to Point Your Domain Name to Brilliant Directories](https://support.brilliantdirectories.com/support/solutions/articles/12000078901-pointing-domain)
• [Resolving 404 Errors on Member Profiles](https://support.brilliantdirectories.com/support/solutions/articles/12000034567-404-member-profiles)

Please test clicking a member profile after saving. Let us know if you encounter any lingering URL redirects!

Warm regards,
AI Technical Support Specialist
Brilliant Directories Support Team`,
      generatedAt: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
      status: "ready"
    },
    thread: [
      {
        sender: "Marcus Vance",
        senderType: "customer",
        timestamp: new Date(Date.now() - 32 * 60 * 1000).toISOString(),
        content: "We pointed our new domain directoryplus.org via A Record yesterday. The home page loads fine, but when clicking on member profile URLs or the login link, users are greeted with a 404 page not found error. How do we update the primary directory URL settings in the BD admin panel to regenerate the permalinks?"
      }
    ]
  },
  {
    id: "TICK-1002",
    customer: {
      name: "Elena Rostova",
      email: "elena@meddirectory.com",
      company: "MedDirectory Global",
      tier: "VIP Enterprise",
      plan: "Enterprise Custom Tier",
      siteUrl: "https://meddirectory.com",
      avatar: "ER"
    },
    subject: "URGENT: Stripe checkout popup failing on mobile devices",
    message: "Our prospective doctors are trying to sign up for our Gold Annual tier on iOS/Safari, but the Stripe payment card modal fails to open upon clicking 'Complete Signup'. We are actively running paid campaigns and losing customers right now. Is this a webhook mismatch or JavaScript issue?",
    category: "Finance & Billing",
    priority: "Urgent",
    status: "needs_review",
    sentiment: "Angry",
    urgencyScore: 97,
    createdAt: new Date(Date.now() - 14 * 60 * 1000).toISOString(),
    aiAnalysis: {
      detectedIssue: "Payment gateway modal blocking on mobile browser / Stripe API key restriction",
      requiredAction: "Verify Stripe Elements integration vs legacy Stripe Checkout, check SSL on checkout page",
      confidence: 0.89,
      escalationRecommended: false,
      recommendedTone: "Urgent, reassuring, immediate troubleshooting steps"
    },
    retrievedSources: [
      {
        title: "Connecting Stripe to Your Brilliant Directories Website",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000045612-stripe-setup",
        section: "Stripe Elements & Mobile Safari Compatibility",
        relevanceScore: 0.95,
        snippet: "Brilliant Directories uses Stripe Elements for inline card processing. If popups fail, check that Webhook Signing Secret is matched and no third-party popup blocking scripts are injected."
      },
      {
        title: "Troubleshooting Failed Signup Transactions",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000098765-failed-signups",
        section: "Webhook Diagnostic Tool",
        relevanceScore: 0.92,
        snippet: "Navigate to Finance > Payment Gateways > Test Credentials. Ensure Live Publishable and Secret Keys have account-level 'Charges: write' permissions."
      }
    ],
    draftReply: {
      subject: "Re: URGENT: Stripe checkout popup failing on mobile devices [TICK-1002]",
      body: `Hi Elena,

We understand this is time-critical with active marketing campaigns running, and we are treating this with top priority.

Brilliant Directories uses the modern **Stripe Elements** inline processing system rather than external popups, so mobile browsers should render fields directly on the signup form without popup blocking. 

Here are the 3 immediate diagnostic checks to resolve this right now:

1. **Verify Stripe Credentials & Connection Status:**
   - In your BD Admin, go to **Finance > Payment Gateways**.
   - Click the green **Test Gateway Connection** button.
   - If a warning appears, verify that both the **Publishable Key** (\`pk_live_...\`) and **Secret Key** (\`sk_live_...\`) are correctly pasted without trailing whitespace.

2. **Check for Custom Code Conflicts in Checkout:**
   - Go to **Settings > Design Settings > Custom CSS / HEAD Code**.
   - If you recently inserted tracking tags (such as Meta Pixel or Google Tag Manager) that trigger on \`form submit\`, they might be intercepting the button click event before Stripe fires. Try temporarily disabling custom footer scripts.

3. **Confirm SSL Certificate Status:**
   - Stripe requires strict HTTPS. Check if the checkout URL exhibits mixed content warnings (HTTP assets on an HTTPS page).

Documentation reference:
• [Connecting Stripe to Brilliant Directories](https://support.brilliantdirectories.com/support/solutions/articles/12000045612-stripe-setup)
• [Payment Gateway Troubleshooting Guide](https://support.brilliantdirectories.com/support/solutions/articles/12000098765-failed-signups)

I have also flagged this ticket with our Senior Platform Engineering team so they can inspect your checkout error logs immediately if the above test doesn't resolve it.

Warm regards,
AI Technical Support Specialist
Brilliant Directories Support Team`,
      generatedAt: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
      status: "ready"
    },
    thread: [
      {
        sender: "Elena Rostova",
        senderType: "customer",
        timestamp: new Date(Date.now() - 14 * 60 * 1000).toISOString(),
        content: "Our prospective doctors are trying to sign up for our Gold Annual tier on iOS/Safari, but the Stripe payment card modal fails to open upon clicking 'Complete Signup'. We are actively running paid campaigns and losing customers right now. Is this a webhook mismatch or JavaScript issue?"
      }
    ]
  },
  {
    id: "TICK-1003",
    customer: {
      name: "David Chen",
      email: "david@dentistfinder.co",
      company: "DentistFinder Co",
      tier: "Starter",
      plan: "Monthly Starter",
      siteUrl: "https://dentistfinder.co",
      avatar: "DC"
    },
    subject: "Best practices for bulk importing 8,500 listings via CSV",
    message: "Hello team, I have an Excel/CSV file containing 8,500 dental clinic records with coordinates, categories, and contact info. Which CSV headers are strictly mandatory for BD member import, and should I upload all 8,500 in a single file or split them?",
    category: "Member Management",
    priority: "Medium",
    status: "auto_drafted",
    sentiment: "Inquisitive",
    urgencyScore: 45,
    createdAt: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
    aiAnalysis: {
      detectedIssue: "Bulk CSV member import specifications and file splitting recommendations",
      requiredAction: "Provide CSV format requirements, mandatory fields, geocoding advice, and 2,000-row batch guideline",
      confidence: 0.98,
      escalationRecommended: false,
      recommendedTone: "Helpful, instructional, structured checklist"
    },
    retrievedSources: [
      {
        title: "How to Import Members via CSV in Brilliant Directories",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000023451-import-members-csv",
        section: "Mandatory CSV Fields & Best Practices",
        relevanceScore: 0.98,
        snippet: "Mandatory fields: Email, First Name, Last Name (or Company Name), and Membership Plan ID. We recommend splitting files over 2,000 records to prevent PHP execution timeout."
      }
    ],
    draftReply: {
      subject: "Re: Best practices for bulk importing 8,500 listings via CSV [TICK-1003]",
      body: `Hi David,

Thanks for reaching out! Bulk importing is one of the fastest ways to populate your directory, and with 8,500 listings, following a few key practices will ensure 100% successful ingestion without server timeouts.

### 1. Mandatory CSV Column Headers
At minimum, your CSV should include:
• **email**: Unique email address for each member.
• **first_name** & **last_name** (or **company_name** for business listings).
• **subscription_id**: The numeric ID of the Membership Plan they belong to (found under **Finance > Membership Plans**).

### 2. Recommended File Splitting
To avoid PHP timeout limits and ensure smooth Google Maps geocoding:
• **Split your 8,500 rows into 4 files of ~2,000 records each.**
• Save files as **CSV (Comma Delimited) with UTF-8 encoding**.

### 3. Geocoding Tips for Addresses
• Include separate columns for \`address1\`, \`city\`, \`state_code\`, \`zip_code\`, and \`country_code\`.
• If you already have \`lat\` and \`lon\` columns, include them to bypass address geocoding API queries!

Detailed step-by-step documentation and sample CSV templates:
• [Member CSV Import Guide & Sample Files](https://support.brilliantdirectories.com/support/solutions/articles/12000023451-import-members-csv)

Let us know if you would like us to review a small 5-row sample before your full upload!

Best regards,
AI Technical Support Specialist
Brilliant Directories Support Team`,
      generatedAt: new Date(Date.now() - 110 * 60 * 1000).toISOString(),
      status: "ready"
    },
    thread: [
      {
        sender: "David Chen",
        senderType: "customer",
        timestamp: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
        content: "Hello team, I have an Excel/CSV file containing 8,500 dental clinic records with coordinates, categories, and contact info. Which CSV headers are strictly mandatory for BD member import, and should I upload all 8,500 in a single file or split them?"
      }
    ]
  },
  {
    id: "TICK-1004",
    customer: {
      name: "Sarah Jenkins",
      email: "sarah@techjobsboard.io",
      company: "TechJobs Board",
      tier: "Pro Developer",
      plan: "VIP Pro Directory",
      siteUrl: "https://techjobsboard.io",
      avatar: "SJ"
    },
    subject: "Where to hook custom PHP widget for Google Tag Manager dataLayer",
    message: "Hi, we are setting up enhanced conversion tracking with Google Tag Manager. We need to pass the member's plan ID and checkout value into the dataLayer array on the checkout thank you page. Where is the recommended hook in BD to insert this snippet without getting overwritten on platform updates?",
    category: "Custom Code & Widgets",
    priority: "Low",
    status: "auto_drafted",
    sentiment: "Inquisitive",
    urgencyScore: 30,
    createdAt: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    aiAnalysis: {
      detectedIssue: "Custom widget creation for GTM dataLayer on signup success page",
      requiredAction: "Explain Custom Widget system in Developer Hub and widget placement in checkout confirmation layout",
      confidence: 0.95,
      escalationRecommended: false,
      recommendedTone: "Technical, concise, developer-oriented"
    },
    retrievedSources: [
      {
        title: "Creating Custom Widgets in Brilliant Directories",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000055432-custom-widgets",
        section: "Custom Widgets & Platform Upgrade Safety",
        relevanceScore: 0.97,
        snippet: "Custom widgets created in Developer Hub > Widget Manager are completely independent of core files and are never overwritten during platform system updates."
      }
    ],
    draftReply: {
      subject: "Re: Where to hook custom PHP widget for Google Tag Manager dataLayer [TICK-1004]",
      body: `Hi Sarah,

Great question! In Brilliant Directories, all custom logic should be created via the **Widget Manager** to ensure your code is update-proof.

Here is the cleanest implementation workflow:

1. **Create a Custom Widget:**
   - Go to **Developer Hub > Widget Manager**.
   - Click **New Widget**.
   - Name it \`gtm_datalayer_checkout\`.
   - In the widget PHP/HTML editor, you can access dynamic user session variables like \`$user_data['plan_id']\` and \`$order['amount']\`.

2. **Hooking into the Signup Thank-You Page:**
   - Go to **Settings > Page Builder > Signup Confirmation**.
   - Insert your custom widget shortcode: \`[widget=gtm_datalayer_checkout]\`.
   - Alternatively, you can include it inside **Settings > Design Settings > Custom Code > HEAD code** wrapped in conditional PHP checking \`if (is_checkout_success_page())\`.

Refer to:
• [Custom Widgets Developer Guide](https://support.brilliantdirectories.com/support/solutions/articles/12000055432-custom-widgets)

Happy coding! Let us know if you need specific variable names for your tracking setup.

Best regards,
AI Technical Support Specialist
Brilliant Directories Support Team`,
      generatedAt: new Date(Date.now() - 210 * 60 * 1000).toISOString(),
      status: "ready"
    },
    thread: [
      {
        sender: "Sarah Jenkins",
        senderType: "customer",
        timestamp: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
        content: "Hi, we are setting up enhanced conversion tracking with Google Tag Manager. We need to pass the member's plan ID and checkout value into the dataLayer array on the checkout thank you page. Where is the recommended hook in BD to insert this snippet without getting overwritten on platform updates?"
      }
    ]
  },
  {
    id: "TICK-1005",
    customer: {
      name: "Tyler Brooks",
      email: "tyler@contractorquote.net",
      company: "ContractorQuote",
      tier: "Starter",
      plan: "Monthly Pro",
      siteUrl: "https://contractorquote.net",
      avatar: "TB"
    },
    subject: "Member lead inquiry notification emails landing in spam",
    message: "Our directory members are complaining that lead notifications sent from our website are ending up in their Outlook and Gmail junk/spam folders. We are using the default website email. How can we configure SPF, DKIM, or connect our SendGrid SMTP account?",
    category: "Email & Notifications",
    priority: "Medium",
    status: "resolved",
    sentiment: "Concerned",
    urgencyScore: 65,
    createdAt: new Date(Date.now() - 26 * 3600 * 1000).toISOString(),
    aiAnalysis: {
      detectedIssue: "Email deliverability & authentication (SPF/DKIM/Custom SMTP)",
      requiredAction: "Guide user to Email Settings & custom SMTP integration with SendGrid/Mailgun",
      confidence: 0.97,
      escalationRecommended: false,
      recommendedTone: "Actionable, clear DNS setup checklist"
    },
    retrievedSources: [
      {
        title: "How to Configure Custom SMTP & Improve Email Deliverability",
        url: "https://support.brilliantdirectories.com/support/solutions/articles/12000067890-smtp-deliverability",
        section: "Connecting Third-Party SMTP Gateways",
        relevanceScore: 0.99,
        snippet: "To prevent spam filtering, navigate to Settings > Email Settings > Custom SMTP. Enter your SendGrid/Mailgun SMTP host, port 587, and API key."
      }
    ],
    draftReply: {
      subject: "Re: Member lead inquiry notification emails landing in spam [TICK-1005]",
      body: `Hi Tyler,

Email deliverability is essential for directories delivering high-value leads to members. When using the default shared server mailer without custom authentication, major providers like Gmail and Outlook frequently route messages to spam.

Connecting a dedicated SMTP provider like SendGrid, Mailgun, or Amazon SES will immediately fix this:

1. **Connect Custom SMTP in BD Admin:**
   - Go to **Settings > Email Settings**.
   - Switch the mailer from **Default Website Mailer** to **Custom SMTP**.
   - Enter your provider credentials (e.g., \`smtp.sendgrid.net\`, port \`587\`, TLS enabled).
   - Click **Send Test Email** to verify instant delivery.

2. **Authenticate Your Domain with DNS Records:**
   - In your domain DNS manager (e.g. Cloudflare, GoDaddy):
   - Add the **SPF record**: \`v=spf1 include:sendgrid.net ~all\`
   - Add the **DKIM CNAME records** provided in your SendGrid dashboard.

Documentation guide:
• [Configuring Custom SMTP in Brilliant Directories](https://support.brilliantdirectories.com/support/solutions/articles/12000067890-smtp-deliverability)

Please let us know if your test email delivers cleanly to your inbox!

Best regards,
AI Technical Support Specialist
Brilliant Directories Support Team`,
      generatedAt: new Date(Date.now() - 25 * 3600 * 1000).toISOString(),
      status: "sent"
    },
    thread: [
      {
        sender: "Tyler Brooks",
        senderType: "customer",
        timestamp: new Date(Date.now() - 26 * 3600 * 1000).toISOString(),
        content: "Our directory members are complaining that lead notifications sent from our website are ending up in their Outlook and Gmail junk/spam folders. We are using the default website email. How can we configure SPF, DKIM, or connect our SendGrid SMTP account?"
      },
      {
        sender: "AI Support Specialist",
        senderType: "agent",
        timestamp: new Date(Date.now() - 25 * 3600 * 1000).toISOString(),
        content: "Detailed SMTP guide sent with SPF/DKIM instructions."
      },
      {
        sender: "Tyler Brooks",
        senderType: "customer",
        timestamp: new Date(Date.now() - 24 * 3600 * 1000).toISOString(),
        content: "Thanks! Connected SendGrid and test email landed straight in the primary inbox. All good now."
      }
    ]
  }
];
