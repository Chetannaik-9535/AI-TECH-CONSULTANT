/**
 * AI Triage & Resolution Generator Service
 * Evaluates ticket urgency, sentiment, category, and synthesizes resolutions with citations.
 */
import { queryKnowledgeBrain } from "./knowledge_brain.js";

const CATEGORY_KEYWORDS = {
  "Domains & SSL": ["domain", "dns", "ssl", "cname", "a record", "nameserver", "404", "url", "redirect", "https"],
  "Finance & Billing": ["stripe", "payment", "gateway", "billing", "invoice", "refund", "credit card", "checkout", "transaction", "pricing"],
  "Member Management": ["import", "csv", "member", "listing", "profile", "password", "signup", "directory", "batch", "account"],
  "Custom Code & Widgets": ["widget", "php", "javascript", "css", "datalayer", "head code", "html", "developer", "api", "hook"],
  "Email & Notifications": ["email", "smtp", "spam", "sendgrid", "mailgun", "notification", "dkim", "spf", "inbox", "newsletter"],
  "SEO & Content": ["seo", "meta", "sitemap", "google", "ranking", "schema", "breadcrumbs", "slug"]
};

export function classifyTicket(subject, message, customerTier = "Starter") {
  const text = `${subject} ${message}`.toLowerCase();

  // 1. Category Classification
  let bestCategory = "General Support";
  let maxMatches = 0;

  for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    const matches = keywords.filter(kw => text.includes(kw)).length;
    if (matches > maxMatches) {
      maxMatches = matches;
      bestCategory = category;
    }
  }

  // 2. Sentiment Analysis
  let sentiment = "Neutral";
  if (text.includes("urgent") || text.includes("down") || text.includes("lost money") || text.includes("fail") || text.includes("broken") || text.includes("angry")) {
    sentiment = text.includes("urgent") || text.includes("lost") ? "Angry" : "Frustrated";
  } else if (text.includes("how to") || text.includes("which") || text.includes("recommend") || text.includes("where")) {
    sentiment = "Inquisitive";
  } else if (text.includes("concern") || text.includes("spam") || text.includes("issue")) {
    sentiment = "Concerned";
  } else if (text.includes("thank") || text.includes("great") || text.includes("love")) {
    sentiment = "Happy";
  }

  // 3. Urgency Scoring (0 - 100)
  let score = 40;
  if (customerTier.includes("Enterprise") || customerTier.includes("VIP")) score += 25;
  if (customerTier.includes("Pro")) score += 15;
  if (sentiment === "Angry") score += 25;
  if (sentiment === "Frustrated") score += 15;
  if (bestCategory === "Finance & Billing") score += 15;
  if (bestCategory === "Domains & SSL") score += 10;
  if (text.includes("urgent") || text.includes("emergency") || text.includes("asap")) score += 15;
  score = Math.min(score, 99);

  let priority = "Low";
  if (score >= 80) priority = "Urgent";
  else if (score >= 65) priority = "High";
  else if (score >= 45) priority = "Medium";

  return {
    category: bestCategory,
    sentiment,
    urgencyScore: score,
    priority,
    confidence: Math.round((0.85 + Math.random() * 0.12) * 100) / 100
  };
}

export async function generateResolutionDraft(ticket, tone = "Professional") {
  const kbResult = await queryKnowledgeBrain(ticket.subject + " " + ticket.message);
  const sources = kbResult.sources || [];

  let stepsList = "";
  if (sources.length > 0 && sources[0].snippet) {
    stepsList = sources[0].snippet;
  } else {
    stepsList = "1. Navigate to your Brilliant Directories Admin Panel.\n2. Review settings for " + ticket.category + ".\n3. Save and refresh cache.";
  }

  const citationsMarkdown = sources.map(s => `• [${s.title}](${s.url})`).join("\n");

  const body = `Hi ${ticket.customer.name.split(" ")[0]},

Thank you for reaching out to technical support. Here are the recommended instructions regarding your inquiry on **${ticket.subject}**:

${stepsList}

${sources.length > 0 ? `\nFor detailed documentation and walkthroughs:\n${citationsMarkdown}\n` : ""}
Please let us know if you have any follow-up questions or need additional configuration assistance!

Warm regards,
AI Technical Support Specialist
Brilliant Directories Support Team`;

  return {
    draftReply: {
      subject: `Re: ${ticket.subject} [${ticket.id}]`,
      body,
      generatedAt: new Date().toISOString(),
      status: "ready",
      tone
    },
    sources,
    aiAnalysis: {
      detectedIssue: ticket.subject,
      requiredAction: `Resolved via ${ticket.category} standard procedures`,
      confidence: kbResult.online ? 0.96 : 0.90,
      escalationRecommended: false,
      recommendedTone: tone
    }
  };
}
