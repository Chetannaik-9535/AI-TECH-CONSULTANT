/**
 * Task 2 Unit Tests: AI Triage & Resolution Generator
 * Tests all categories, sentiments, urgency scores, customer tiers, and draft generation.
 */
import assert from "node:assert/strict";
import { classifyTicket, generateResolutionDraft } from "../services/triage.js";

console.log("▶ Running Task 2 Triage Unit Tests...");

// ─── Test 1: Category Classification ─────────────────────────────────
console.log("  [1/4] Testing Category Keyword Classification...");

const catDomains = classifyTicket("Need help pointing domain", "Our DNS A-record and SSL certificate are not working");
assert.equal(catDomains.category, "Domains & SSL");

const catBilling = classifyTicket("Stripe checkout error", "Credit card payment gateway failed during invoice refund");
assert.equal(catBilling.category, "Finance & Billing");

const catMembers = classifyTicket("CSV Member Upload Issue", "Cannot import member listing profile batch from CSV");
assert.equal(catMembers.category, "Member Management");

const catWidgets = classifyTicket("Custom PHP Widget Crash", "My javascript widget hook and datalayer broke after update");
assert.equal(catWidgets.category, "Custom Code & Widgets");

const catEmail = classifyTicket("SMTP Deliverability issue", "Sendgrid emails going to spam folder, need SPF and DKIM setup");
assert.equal(catEmail.category, "Email & Notifications");

const catGeneral = classifyTicket("Hello there", "Just checking in with your support desk");
assert.equal(catGeneral.category, "General Support");

console.log("    ✓ Category Classification passed for all 6 domains + fallback");

// ─── Test 2: Sentiment Detection ─────────────────────────────────────
console.log("  [2/4] Testing Sentiment Detection...");

const sentAngry = classifyTicket("URGENT: Lost money on checkout", "System is down and we lost money on live transactions!");
assert.equal(sentAngry.sentiment, "Angry");

const sentFrustrated = classifyTicket("Checkout broken", "This payment gateway fail is broken again");
assert.equal(sentFrustrated.sentiment, "Frustrated");

const sentInquisitive = classifyTicket("How to set up domain?", "Where can I find which DNS settings to recommend?");
assert.equal(sentInquisitive.sentiment, "Inquisitive");

const sentConcerned = classifyTicket("Spam warning", "I have a concern regarding spam signups on my issue tracker");
assert.equal(sentConcerned.sentiment, "Concerned");

const sentHappy = classifyTicket("Thank you!", "Great work, love the platform and thank you for the help");
assert.equal(sentHappy.sentiment, "Happy");

const sentNeutral = classifyTicket("Domain records updated", "A record points to 54.208.192.173");
assert.equal(sentNeutral.sentiment, "Neutral");

console.log("    ✓ Sentiment Detection passed across all emotional states");

// ─── Test 3: SLA Urgency Scoring & Priority Tiers ────────────────────
console.log("  [3/4] Testing Urgency Scoring & Customer Tier SLAs...");

// VIP Enterprise with Urgent Keywords
const vipUrgent = classifyTicket("EMERGENCY: Payment gateway broken", "Stripe payment fail asap", "VIP Enterprise");
assert.ok(vipUrgent.urgencyScore >= 80, `Expected score >= 80, got ${vipUrgent.urgencyScore}`);
assert.equal(vipUrgent.priority, "Urgent");

// Pro Tier Medium/High
const proBilling = classifyTicket("Invoice question", "Stripe billing inquiry", "Pro");
assert.ok(proBilling.urgencyScore >= 60, `Expected score >= 60, got ${proBilling.urgencyScore}`);

// Starter Low
const starterGeneral = classifyTicket("General question", "Just asking for information", "Starter");
assert.ok(starterGeneral.urgencyScore <= 50, `Expected score <= 50, got ${starterGeneral.urgencyScore}`);

// Confidence bounds check
assert.ok(vipUrgent.confidence >= 0.85 && vipUrgent.confidence <= 1.0, "Confidence score out of range");

console.log("    ✓ Urgency Scoring & Priority Tiers passed");

// ─── Test 4: Resolution Draft Generation ─────────────────────────────
console.log("  [4/4] Testing Resolution Draft Synthesis...");

const mockTicket = {
  id: "TICK-TEST-101",
  customer: { name: "Sarah Connor", email: "sarah@skynet.com", tier: "VIP Enterprise" },
  subject: "How to Point Domain Name",
  message: "What A-record and IP address should I configure for DNS?",
  category: "Domains & SSL"
};

const tones = ["Professional", "Empathetic", "Technical", "Step-by-Step"];
for (const tone of tones) {
  const draft = await generateResolutionDraft(mockTicket, tone);
  assert.ok(draft.draftReply, `Missing draftReply for tone ${tone}`);
  assert.equal(draft.draftReply.tone, tone);
  assert.ok(draft.draftReply.subject.includes("TICK-TEST-101"), "Subject should include ticket ID");
  assert.ok(draft.draftReply.body.includes("Sarah"), "Body should greet customer by first name");
  assert.ok(draft.draftReply.body.length > 50, "Body should contain substantive content");
}

console.log("    ✓ Draft Synthesis passed across all 4 tone modes");
console.log("🎉 All Task 2 Triage Unit Tests PASSED successfully!\n");
