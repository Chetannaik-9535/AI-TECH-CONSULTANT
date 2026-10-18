/**
 * Task 2: Inbox Agent Server
 * REST API & Web Dashboard Host for AI Tech Consultant Ticket Operations
 */
import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import { SEED_TICKETS } from "./data/seed_tickets.js";
import { classifyTicket, generateResolutionDraft } from "./services/triage.js";
import { checkKnowledgeBrainHealth, forwardEscalationToKB } from "./services/knowledge_brain.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.INBOX_AGENT_PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, "public")));

// In-memory ticket storage initialized from seed
let tickets = JSON.parse(JSON.stringify(SEED_TICKETS));

// ─── API Routes ──────────────────────────────────────────────────────

// 1. Health check & Knowledge Brain status
app.get("/api/health", async (req, res) => {
  const kbStatus = await checkKnowledgeBrainHealth();
  res.json({
    status: "healthy",
    service: "inbox-agent",
    port: PORT,
    ticketsCount: tickets.length,
    knowledgeBrain: kbStatus
  });
});

// 2. Metrics & Dashboard Stats
app.get("/api/stats", (req, res) => {
  const total = tickets.length;
  const needsReview = tickets.filter(t => t.status === "needs_review").length;
  const autoDrafted = tickets.filter(t => t.status === "auto_drafted").length;
  const escalated = tickets.filter(t => t.status === "escalated").length;
  const resolved = tickets.filter(t => t.status === "resolved").length;

  const urgentCount = tickets.filter(t => t.priority === "Urgent" && t.status !== "resolved").length;
  const highCount = tickets.filter(t => t.priority === "High" && t.status !== "resolved").length;

  // Category counts
  const categories = {};
  for (const t of tickets) {
    categories[t.category] = (categories[t.category] || 0) + 1;
  }

  res.json({
    total,
    needsReview,
    autoDrafted,
    escalated,
    resolved,
    urgentCount,
    highCount,
    deflectionRate: Math.round(((autoDrafted + resolved) / Math.max(total, 1)) * 100),
    avgResolutionTime: "1.4s (AI) vs 4.8h (Human)",
    categories
  });
});

// 3. List all tickets with filtering
app.get("/api/tickets", (req, res) => {
  const { status, category, priority, search } = req.query;
  let filtered = [...tickets];

  if (status && status !== "all") {
    filtered = filtered.filter(t => t.status === status);
  }
  if (category && category !== "all") {
    filtered = filtered.filter(t => t.category === category);
  }
  if (priority && priority !== "all") {
    filtered = filtered.filter(t => t.priority === priority);
  }
  if (search) {
    const s = search.toLowerCase();
    filtered = filtered.filter(t =>
      t.subject.toLowerCase().includes(s) ||
      t.message.toLowerCase().includes(s) ||
      t.customer.name.toLowerCase().includes(s) ||
      t.customer.company.toLowerCase().includes(s) ||
      t.id.toLowerCase().includes(s)
    );
  }

  // Sort: unresolved urgent first, then by date descending
  filtered.sort((a, b) => {
    if (a.status !== "resolved" && b.status === "resolved") return -1;
    if (a.status === "resolved" && b.status !== "resolved") return 1;
    return new Date(b.createdAt) - new Date(a.createdAt);
  });

  res.json(filtered);
});

// 4. Get ticket by ID
app.get("/api/tickets/:id", (req, res) => {
  const ticket = tickets.find(t => t.id === req.params.id);
  if (!ticket) {
    return res.status(404).json({ error: "Ticket not found" });
  }
  res.json(ticket);
});

// 5. Ingest / Simulate a new ticket
app.post("/api/tickets", async (req, res) => {
  const { customer, subject, message } = req.body;
  if (!subject || !message) {
    return res.status(400).json({ error: "Subject and message are required" });
  }

  const id = `TICK-${1000 + tickets.length + 1}`;
  const tier = customer?.tier || "Starter";

  // Automated AI Triage
  const triage = classifyTicket(subject, message, tier);

  const newTicket = {
    id,
    customer: {
      name: customer?.name || "Alex Morgan",
      email: customer?.email || "alex@customerdirectory.com",
      company: customer?.company || "LocalBiz Finder",
      tier: tier,
      plan: customer?.plan || "Professional Directory Plan",
      siteUrl: customer?.siteUrl || "https://customerdirectory.com",
      avatar: (customer?.name || "AM").split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2)
    },
    subject,
    message,
    category: triage.category,
    priority: triage.priority,
    status: "needs_review",
    sentiment: triage.sentiment,
    urgencyScore: triage.urgencyScore,
    createdAt: new Date().toISOString(),
    aiAnalysis: {
      detectedIssue: subject,
      requiredAction: `Review ${triage.category} and verify draft response`,
      confidence: triage.confidence,
      escalationRecommended: triage.urgencyScore > 90,
      recommendedTone: "Professional, instructional"
    },
    thread: [
      {
        sender: customer?.name || "Alex Morgan",
        senderType: "customer",
        timestamp: new Date().toISOString(),
        content: message
      }
    ]
  };

  // Generate automated resolution draft immediately
  try {
    const draftData = await generateResolutionDraft(newTicket);
    newTicket.draftReply = draftData.draftReply;
    newTicket.retrievedSources = draftData.sources;
    newTicket.status = "auto_drafted";
  } catch (err) {
    console.error("Draft generation error:", err);
  }

  tickets.unshift(newTicket);
  res.status(201).json(newTicket);
});

// 6. Regenerate draft with customized tone
app.post("/api/tickets/:id/draft", async (req, res) => {
  const ticket = tickets.find(t => t.id === req.params.id);
  if (!ticket) return res.status(404).json({ error: "Ticket not found" });

  const { tone = "Professional", customInstructions = "" } = req.body;
  const result = await generateResolutionDraft(ticket, tone);

  ticket.draftReply = result.draftReply;
  if (customInstructions) {
    ticket.draftReply.body += `\n\n*Note*: ${customInstructions}`;
  }
  ticket.retrievedSources = result.sources;
  ticket.status = "auto_drafted";

  res.json(ticket);
});

// 7. Approve & Send resolution
app.post("/api/tickets/:id/send", (req, res) => {
  const ticket = tickets.find(t => t.id === req.params.id);
  if (!ticket) return res.status(404).json({ error: "Ticket not found" });

  const { finalBody } = req.body;
  const replyContent = finalBody || ticket.draftReply?.body || "Inquiry resolved.";

  ticket.thread.push({
    sender: "AI Technical Support Specialist",
    senderType: "agent",
    timestamp: new Date().toISOString(),
    content: replyContent
  });

  ticket.status = "resolved";
  if (ticket.draftReply) {
    ticket.draftReply.status = "sent";
    ticket.draftReply.sentAt = new Date().toISOString();
  }

  res.json({ success: true, ticket });
});

// 8. Escalate ticket to Human Developer / Knowledge Brain
app.post("/api/tickets/:id/escalate", async (req, res) => {
  const ticket = tickets.find(t => t.id === req.params.id);
  if (!ticket) return res.status(404).json({ error: "Ticket not found" });

  const { reason = "requires_senior_developer", note = "" } = req.body;
  ticket.status = "escalated";
  ticket.escalatedAt = new Date().toISOString();
  ticket.escalationReason = reason;
  ticket.escalationNote = note;

  // Forward to Knowledge Brain /escalations endpoint
  const kbEscalation = await forwardEscalationToKB(
    ticket.id,
    reason,
    ticket.subject,
    `${note}. Customer: ${ticket.customer.name} (${ticket.customer.email})`
  );
  ticket.kbEscalationId = kbEscalation?.id;

  ticket.thread.push({
    sender: "System Event",
    senderType: "system",
    timestamp: new Date().toISOString(),
    content: `🚨 Ticket escalated to Senior Platform Engineering. Reason: ${reason}. ${note}`
  });

  res.json({ success: true, ticket });
});

// 9. Reset seed data
app.post("/api/tickets/reset", (req, res) => {
  tickets = JSON.parse(JSON.stringify(SEED_TICKETS));
  res.json({ message: "Tickets reset to initial state", count: tickets.length });
});

// Catch-all HTML fallback
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

export { app };

let serverInstance = null;
export function startServer(port = PORT) {
  return new Promise((resolve) => {
    serverInstance = app.listen(port, () => {
      console.log(`===============================================`);
      console.log(`🤖 AI Tech Consultant - Inbox Agent`);
      console.log(`🚀 Live Dashboard: http://localhost:${port}`);
      console.log(`🔗 Knowledge Brain: http://localhost:8000`);
      console.log(`===============================================`);
      resolve(serverInstance);
    });
  });
}

// Auto-start if run directly from terminal
const isMain = process.argv[1] && (
  process.argv[1].endsWith("server.js") || 
  fileURLToPath(import.meta.url) === path.resolve(process.argv[1])
);
if (isMain) {
  startServer(PORT);
}

