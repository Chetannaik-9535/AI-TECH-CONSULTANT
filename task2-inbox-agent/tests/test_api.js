/**
 * Task 2 Integration Tests: Inbox Agent REST API Endpoints
 * Tests live server on http://localhost:3000 across all routes and conditions.
 */
import assert from "node:assert/strict";

const BASE_URL = process.env.INBOX_AGENT_URL || "http://localhost:3000";

console.log(`▶ Running Task 2 API Integration Tests against ${BASE_URL}...`);

// ─── Test 1: Health & Knowledge Brain Connectivity ───────────────────
console.log("  [1/8] Testing GET /api/health...");
const healthRes = await fetch(`${BASE_URL}/api/health`);
assert.equal(healthRes.status, 200, "Health endpoint should return 200");
const healthData = await healthRes.json();
assert.equal(healthData.status, "healthy");
assert.equal(healthData.service, "inbox-agent");
assert.ok(healthData.ticketsCount > 0, "Should have initialized tickets");
assert.ok(healthData.knowledgeBrain, "Should report knowledgeBrain status");
console.log(`    ✓ Health OK: ${healthData.ticketsCount} tickets, Knowledge Brain online=${healthData.knowledgeBrain.online}`);

// ─── Test 2: Dashboard Statistics ────────────────────────────────────
console.log("  [2/8] Testing GET /api/stats...");
const statsRes = await fetch(`${BASE_URL}/api/stats`);
assert.equal(statsRes.status, 200);
const statsData = await statsRes.json();
assert.ok("total" in statsData);
assert.ok("deflectionRate" in statsData);
assert.ok("categories" in statsData);
assert.ok(statsData.total > 0, "Total tickets should be > 0");
console.log(`    ✓ Stats OK: total=${statsData.total}, deflectionRate=${statsData.deflectionRate}%`);

// ─── Test 3: List Tickets with Filtering & Search ────────────────────
console.log("  [3/8] Testing GET /api/tickets with filters...");
const allRes = await fetch(`${BASE_URL}/api/tickets`);
const allTickets = await allRes.json();
assert.ok(Array.isArray(allTickets));

// Filter by status
const openRes = await fetch(`${BASE_URL}/api/tickets?status=needs_review`);
const openTickets = await openRes.json();
assert.ok(openTickets.every(t => t.status === "needs_review"));

// Search filter
const searchRes = await fetch(`${BASE_URL}/api/tickets?search=stripe`);
const searchTickets = await searchRes.json();
assert.ok(searchTickets.length > 0, "Search for 'stripe' should find relevant tickets");

console.log(`    ✓ Ticket filtering & search verified (found ${searchTickets.length} tickets matching 'stripe')`);

// ─── Test 4: Get Ticket by ID & 404 Condition ────────────────────────
console.log("  [4/8] Testing GET /api/tickets/:id (success & 404)...");
const firstTicketId = allTickets[0].id;
const singleRes = await fetch(`${BASE_URL}/api/tickets/${firstTicketId}`);
assert.equal(singleRes.status, 200);
const singleTicket = await singleRes.json();
assert.equal(singleTicket.id, firstTicketId);

const notFoundRes = await fetch(`${BASE_URL}/api/tickets/TICK-NONEXISTENT-9999`);
assert.equal(notFoundRes.status, 404);
console.log("    ✓ Get ticket by ID and 404 error condition verified");

// ─── Test 5: Ingest New Ticket & Input Validation ────────────────────
console.log("  [5/8] Testing POST /api/tickets (Validation & Ingestion)...");

// Bad request (missing subject/message)
const badRes = await fetch(`${BASE_URL}/api/tickets`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ customer: { name: "Test" } })
});
assert.equal(badRes.status, 400, "Missing fields should return 400");

// Valid new ticket
const newTicketPayload = {
  customer: {
    name: "Elena Rostova",
    email: "elena@eurobiz.com",
    company: "EuroBiz Hub",
    tier: "VIP Enterprise"
  },
  subject: "Stripe Webhook Fails on Recurring Payments",
  message: "Our live customers are reporting failed renewals on their credit cards. Stripe webhook endpoint shows 500 error."
};

const createRes = await fetch(`${BASE_URL}/api/tickets`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(newTicketPayload)
});
assert.equal(createRes.status, 201);
const createdTicket = await createRes.json();
assert.ok(createdTicket.id.startsWith("TICK-"));
assert.equal(createdTicket.category, "Finance & Billing");
assert.equal(createdTicket.priority, "Urgent");
assert.ok(createdTicket.draftReply, "Auto-draft should be generated immediately");
console.log(`    ✓ Ticket creation & auto-triage passed (ID: ${createdTicket.id}, Priority: ${createdTicket.priority})`);

// ─── Test 6: Regenerate Draft with Custom Tone ───────────────────────
console.log("  [6/8] Testing POST /api/tickets/:id/draft (Tone regeneration)...");
const draftRes = await fetch(`${BASE_URL}/api/tickets/${createdTicket.id}/draft`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    tone: "Empathetic",
    customInstructions: "Prioritize urgency and reassure customer about data safety."
  })
});
assert.equal(draftRes.status, 200);
const updatedTicket = await draftRes.json();
assert.equal(updatedTicket.draftReply.tone, "Empathetic");
assert.ok(updatedTicket.draftReply.body.includes("Prioritize urgency"), "Custom instructions should be included");
console.log("    ✓ Draft tone regeneration verified");

// ─── Test 7: Approve & Send Resolution ───────────────────────────────
console.log("  [7/8] Testing POST /api/tickets/:id/send (Resolution delivery)...");
const sendRes = await fetch(`${BASE_URL}/api/tickets/${createdTicket.id}/send`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    finalBody: "Your Stripe webhook signing secret has been verified and synced. All renewals are processing smoothly."
  })
});
assert.equal(sendRes.status, 200);
const sendData = await sendRes.json();
assert.equal(sendData.ticket.status, "resolved");
assert.equal(sendData.ticket.draftReply.status, "sent");
assert.ok(sendData.ticket.thread.some(msg => msg.senderType === "agent"));
console.log("    ✓ Resolution approved and sent (Ticket status: resolved)");

// ─── Test 8: Ticket Escalation Workflow ──────────────────────────────
console.log("  [8/8] Testing POST /api/tickets/:id/escalate (Escalation to Task 1)...");
const escalateRes = await fetch(`${BASE_URL}/api/tickets/${firstTicketId}/escalate`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    reason: "core_php_widget_segfault",
    note: "Customer widget causes server-side 502 gateway timeouts."
  })
});
assert.equal(escalateRes.status, 200);
const escData = await escalateRes.json();
assert.equal(escData.ticket.status, "escalated");
assert.equal(escData.ticket.escalationReason, "core_php_widget_segfault");
assert.ok(escData.ticket.thread.some(msg => msg.senderType === "system"));
console.log(`    ✓ Escalation workflow passed (kbEscalationId: ${escData.ticket.kbEscalationId || "forwarded"})`);

// ─── Cleanup: Reset Data ─────────────────────────────────────────────
console.log("  [Cleanup] Resetting tickets data...");
const resetRes = await fetch(`${BASE_URL}/api/tickets/reset`, { method: "POST" });
assert.equal(resetRes.status, 200);
console.log("    ✓ Reset complete.");

console.log("🎉 All Task 2 API Integration Tests PASSED successfully!\n");
