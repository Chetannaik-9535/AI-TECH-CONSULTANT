/**
 * AI Tech Consultant - Inbox Agent Frontend
 * Dynamic ticket feed, Knowledge Brain grounding, resolution approval & escalation router
 */

// ─── Application State ───────────────────────────────────────────────────────
const state = {
  tickets: [],
  selectedTicketId: null,
  filters: {
    status: "all",
    category: "all",
    priority: "all",
    search: ""
  },
  stats: {},
  kbStatus: { online: false }
};

// Preset Scenarios for Rapid Simulation
const PRESET_SCENARIOS = {
  ssl: {
    name: "Jason Bradley",
    email: "jason@propertymarket.net",
    company: "PropertyMarket Hub",
    tier: "VIP Enterprise",
    subject: "SSL activated but browser shows 'Not Secure' mixed content warning",
    message: "We installed the BD SSL certificate on propertymarket.net this morning. However, Google Chrome still displays 'Not Secure' with mixed content warnings because logo and hero image URLs are still loaded via http://. Where do we update the media URLs?"
  },
  stripe: {
    name: "Sophia Martinez",
    email: "sophia@wellnessdirectory.io",
    company: "Wellness Directory",
    tier: "Directory Pro",
    subject: "Stripe recurring subscription not canceling when member downgrades",
    message: "When our members downgrade from the Premium tier to the Free tier, their profile updates in BD, but their Stripe recurring payment is not automatically stopped in Stripe. How do we ensure webhook synchronization handles downgrade cancellations?"
  },
  csv: {
    name: "Michael Chang",
    email: "mchang@autoexperts.org",
    company: "AutoExperts Network",
    tier: "Starter",
    subject: "Errors when importing coordinates in CSV file",
    message: "We have 4,000 mechanic listings with latitude and longitude columns in our CSV. What are the exact column header names Brilliant Directories expects for lat and long so Google Maps recognizes them immediately?"
  },
  widget: {
    name: "Liam O'Connor",
    email: "liam@techjobs.ie",
    company: "Irish Tech Jobs",
    tier: "VIP Enterprise",
    subject: "How to conditionally show custom sidebar banner only to logged-in members",
    message: "We built a custom widget for our sidebar. What PHP session variable or helper function should we check in our widget code to only render the banner if the viewing user has an active member session?"
  }
};

// ─── Initialization ──────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadInitialData();
  // Poll metrics every 15s
  setInterval(loadStats, 15000);
  setInterval(checkKBStatus, 20000);
});

async function loadInitialData() {
  await Promise.all([checkKBStatus(), loadStats(), loadTickets()]);
}

// ─── API Interactions ────────────────────────────────────────────────────────

async function loadTickets() {
  try {
    const params = new URLSearchParams();
    if (state.filters.status !== "all") params.append("status", state.filters.status);
    if (state.filters.category !== "all") params.append("category", state.filters.category);
    if (state.filters.priority !== "all") params.append("priority", state.filters.priority);
    if (state.filters.search) params.append("search", state.filters.search);

    const res = await fetch(`/api/tickets?${params.toString()}`);
    if (res.ok) {
      state.tickets = await res.json();
      renderTicketFeed();

      // Auto-select first ticket if none or current not found
      if (state.tickets.length > 0) {
        if (!state.selectedTicketId || !state.tickets.some(t => t.id === state.selectedTicketId)) {
          selectTicket(state.tickets[0].id);
        } else {
          renderTicketDetail();
        }
      } else {
        state.selectedTicketId = null;
        renderTicketDetail();
      }
    }
  } catch (err) {
    console.error("Failed to load tickets:", err);
  }
}

async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    if (res.ok) {
      state.stats = await res.json();
      updateMetricPills();
    }
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
}

async function checkKBStatus() {
  const badge = document.getElementById("kb-status-badge");
  const text = document.getElementById("kb-status-text");
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      state.kbStatus = data.knowledgeBrain || { online: false };
      if (state.kbStatus.online) {
        badge.classList.remove("offline");
        text.textContent = `Knowledge Brain: Active (${state.kbStatus.total_articles || "Ready"})`;
      } else {
        badge.classList.add("offline");
        text.textContent = "Knowledge Brain: Offline (Fallback Mode)";
      }
      return;
    }
  } catch (err) {
    // Offline
  }
  badge.classList.add("offline");
  text.textContent = "Knowledge Brain: Offline (Fallback Mode)";
}

// ─── Rendering Methods ───────────────────────────────────────────────────────

function renderTicketFeed() {
  const container = document.getElementById("ticket-cards-list");
  const countText = document.getElementById("feed-count-text");
  countText.textContent = `Showing ${state.tickets.length} inquiries`;

  if (state.tickets.length === 0) {
    container.innerHTML = `
      <div class="empty-feed" style="text-align:center; padding: 40px 16px; color: var(--text-dim);">
        <p>No tickets matching current filters.</p>
      </div>`;
    return;
  }

  container.innerHTML = state.tickets.map(t => {
    const isSelected = t.id === state.selectedTicketId;
    const timeAgo = formatTimeAgo(t.createdAt);
    const pClass = `tag-${t.priority.toLowerCase()}`;
    const initials = (t.customer?.name || "AM").split(" ").map(w => w[0]).join("").slice(0, 2);

    return `
      <article class="ticket-card ${isSelected ? 'selected' : ''}" data-ticket-id="${t.id}">
        <div class="card-top">
          <div class="card-sender">
            <div class="mini-avatar">${initials}</div>
            <span class="sender-name">${escapeHtml(t.customer?.name || 'Customer')}</span>
          </div>
          <span class="card-time">${timeAgo}</span>
        </div>
        <h4 class="card-subject">${escapeHtml(t.subject)}</h4>
        <p class="card-preview">${escapeHtml(t.message)}</p>
        <div class="card-bottom-tags">
          <div class="tags-left">
            <span class="tag-badge ${pClass}">${t.priority}</span>
            <span class="tag-badge" style="background: rgba(255,255,255,0.05); color: var(--text-muted);">${escapeHtml(t.category)}</span>
          </div>
          <span class="sentiment-dot">${t.sentiment || 'Neutral'}</span>
        </div>
      </article>`;
  }).join("");

  // Attach card click handlers
  container.querySelectorAll(".ticket-card").forEach(card => {
    card.addEventListener("click", () => {
      const id = card.getAttribute("data-ticket-id");
      selectTicket(id);
    });
  });
}

function selectTicket(id) {
  state.selectedTicketId = id;
  // Update card selected class
  document.querySelectorAll(".ticket-card").forEach(c => {
    c.classList.toggle("selected", c.getAttribute("data-ticket-id") === id);
  });
  renderTicketDetail();
}

function renderTicketDetail() {
  const emptyView = document.getElementById("empty-detail");
  const activeView = document.getElementById("active-detail");

  const ticket = state.tickets.find(t => t.id === state.selectedTicketId);
  if (!ticket) {
    emptyView.style.display = "block";
    activeView.style.display = "none";
    return;
  }

  emptyView.style.display = "none";
  activeView.style.display = "flex";

  // Header meta
  document.getElementById("det-id").textContent = ticket.id;
  const statusBadge = document.getElementById("det-status-badge");
  statusBadge.textContent = formatStatusLabel(ticket.status);
  statusBadge.className = `badge ${getStatusBadgeClass(ticket.status)}`;

  const prioBadge = document.getElementById("det-priority-badge");
  prioBadge.textContent = ticket.priority;
  prioBadge.className = `badge tag-${ticket.priority.toLowerCase()}`;

  document.getElementById("det-category-badge").textContent = ticket.category;
  document.getElementById("det-subject").textContent = ticket.subject;

  // Customer identity
  const initials = (ticket.customer?.name || "AM").split(" ").map(w => w[0]).join("").slice(0, 2);
  document.getElementById("det-avatar").textContent = initials;
  document.getElementById("det-customer-name").textContent = ticket.customer?.name || "Customer";
  document.getElementById("det-customer-tier").textContent = ticket.customer?.tier || "Starter Tier";
  document.getElementById("det-customer-email").textContent = ticket.customer?.email || "";
  document.getElementById("det-customer-company").textContent = ticket.customer?.company || "Member Directory";
  const urlLink = document.getElementById("det-customer-url");
  urlLink.textContent = ticket.customer?.siteUrl ? ticket.customer.siteUrl.replace(/^https?:\/\//, "") : "";
  urlLink.href = ticket.customer?.siteUrl || "#";

  // Urgency
  const score = ticket.urgencyScore || 50;
  document.getElementById("det-urgency-num").textContent = `${score}/100`;
  document.getElementById("det-urgency-fill").style.width = `${score}%`;

  // AI Triage
  const conf = ticket.aiAnalysis?.confidence ? Math.round(ticket.aiAnalysis.confidence * 100) : 92;
  document.getElementById("det-confidence").textContent = `${conf}% Confidence`;
  document.getElementById("det-triage-issue").textContent = ticket.aiAnalysis?.detectedIssue || ticket.subject;
  document.getElementById("det-sentiment-pill").textContent = ticket.sentiment || "Neutral";
  document.getElementById("det-triage-action").textContent = ticket.aiAnalysis?.requiredAction || "Review Knowledge Base articles and verify response";

  // Sources
  const sourcesContainer = document.getElementById("det-sources-list");
  const sources = ticket.retrievedSources || [];
  if (sources.length === 0) {
    sourcesContainer.innerHTML = `<p style="font-size:0.8rem; color:var(--text-dim);">No specific article sources linked yet.</p>`;
  } else {
    sourcesContainer.innerHTML = sources.map(s => `
      <div class="source-item">
        <div class="source-header">
          <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer" class="source-link">
            📖 ${escapeHtml(s.title)}
          </a>
          <span class="source-score">${Math.round((s.relevanceScore || 0.9) * 100)}% match</span>
        </div>
        <p class="source-snippet">${escapeHtml(s.snippet || s.section || '')}</p>
      </div>`).join("");
  }

  // Thread
  const threadContainer = document.getElementById("det-thread-messages");
  const thread = ticket.thread || [];
  threadContainer.innerHTML = thread.map(msg => {
    const isCustomer = msg.senderType === "customer";
    const isAgent = msg.senderType === "agent";
    const typeClass = isCustomer ? "customer" : (isAgent ? "agent" : "system");
    const senderTitle = isCustomer ? (ticket.customer?.name || "Customer") : (isAgent ? "AI Technical Support Specialist" : "Platform Alert");

    return `
      <div class="thread-msg ${typeClass}">
        <div class="msg-header">
          <strong>${escapeHtml(senderTitle)}</strong>
          <span>${formatTimeAgo(msg.timestamp)}</span>
        </div>
        <div>${escapeHtml(msg.content)}</div>
      </div>`;
  }).join("");

  // Resolution Composer
  const replyText = document.getElementById("reply-textarea");
  replyText.value = ticket.draftReply?.body || "";
  document.getElementById("det-draft-status").textContent = ticket.status === "resolved" ? "Sent & Resolved" : "Ready for Review";

  const sendBtn = document.getElementById("btn-approve-send");
  if (ticket.status === "resolved") {
    sendBtn.disabled = true;
    sendBtn.innerHTML = "✓ Already Sent";
  } else {
    sendBtn.disabled = false;
    sendBtn.innerHTML = `
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <line x1="22" y1="2" x2="11" y2="13"></line>
        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
      </svg>
      Approve &amp; Send Reply`;
  }
}

function updateMetricPills() {
  document.getElementById("count-needs-review").textContent = state.stats.needsReview || 0;
  document.getElementById("count-auto-drafted").textContent = state.stats.autoDrafted || 0;
  document.getElementById("count-escalated").textContent = state.stats.escalated || 0;
  document.getElementById("count-resolved").textContent = state.stats.resolved || 0;

  document.getElementById("badge-total").textContent = state.stats.total || 0;
  document.getElementById("nav-badge-needs-review").textContent = state.stats.needsReview || 0;
  document.getElementById("nav-badge-auto-drafted").textContent = state.stats.autoDrafted || 0;
  document.getElementById("nav-badge-escalated").textContent = state.stats.escalated || 0;
  document.getElementById("nav-badge-resolved").textContent = state.stats.resolved || 0;
}

// ─── Actions & Event Listeners ───────────────────────────────────────────────

function initEventListeners() {
  // Navigation sidebar filters
  document.querySelectorAll("[data-filter-status]").forEach(item => {
    item.addEventListener("click", () => {
      document.querySelectorAll("[data-filter-status]").forEach(i => i.classList.remove("active"));
      item.classList.add("active");
      state.filters.status = item.getAttribute("data-filter-status");
      loadTickets();
    });
  });

  // Top header quick metric pill filter triggers
  const pillStatusMap = [
    { id: "pill-needs-review", status: "needs_review" },
    { id: "pill-auto-drafted", status: "auto_drafted" },
    { id: "pill-escalated", status: "escalated" },
    { id: "pill-resolved", status: "resolved" }
  ];
  pillStatusMap.forEach(({ id, status }) => {
    const el = document.getElementById(id);
    if (el) {
      el.style.cursor = "pointer";
      el.addEventListener("click", () => {
        document.querySelectorAll("[data-filter-status]").forEach(i => {
          i.classList.toggle("active", i.getAttribute("data-filter-status") === status);
        });
        state.filters.status = status;
        loadTickets();
      });
    }
  });

  // Category chips
  document.querySelectorAll("[data-category]").forEach(chip => {
    chip.addEventListener("click", () => {
      document.querySelectorAll("[data-category]").forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      state.filters.category = chip.getAttribute("data-category");
      loadTickets();
    });
  });

  // Priority tags
  document.querySelectorAll("[data-priority]").forEach(tag => {
    tag.addEventListener("click", () => {
      document.querySelectorAll("[data-priority]").forEach(t => t.classList.remove("active"));
      tag.classList.add("active");
      state.filters.priority = tag.getAttribute("data-priority");
      loadTickets();
    });
  });

  // Search input
  const searchInput = document.getElementById("search-input");
  const clearBtn = document.getElementById("btn-clear-search");
  let searchTimeout = null;
  searchInput.addEventListener("input", (e) => {
    clearTimeout(searchTimeout);
    state.filters.search = e.target.value.trim();
    clearBtn.style.display = state.filters.search ? "block" : "none";
    searchTimeout = setTimeout(() => loadTickets(), 250);
  });
  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    state.filters.search = "";
    clearBtn.style.display = "none";
    loadTickets();
  });

  // Approve & Send button
  document.getElementById("btn-approve-send").addEventListener("click", handleSendResolution);

  // Save changes button
  document.getElementById("btn-save-draft").addEventListener("click", () => {
    const ticket = state.tickets.find(t => t.id === state.selectedTicketId);
    if (ticket && ticket.draftReply) {
      ticket.draftReply.body = document.getElementById("reply-textarea").value;
      showToast("Draft changes saved locally", "info");
    }
  });

  // Regenerate draft button & Tone select change
  document.getElementById("btn-regen-draft").addEventListener("click", handleRegenerateDraft);
  const toneSelect = document.getElementById("tone-select");
  if (toneSelect) {
    toneSelect.addEventListener("change", handleRegenerateDraft);
  }

  // Reset Demo Data
  document.getElementById("btn-reset-demo").addEventListener("click", async () => {
    if (confirm("Reset inbox tickets back to initial seed data?")) {
      const res = await fetch("/api/tickets/reset", { method: "POST" });
      if (res.ok) {
        showToast("Demo data reset to default", "info");
        loadInitialData();
      }
    }
  });

  // Modal: Simulate Ticket
  const simModal = document.getElementById("modal-simulate");
  document.getElementById("btn-simulate-ticket").addEventListener("click", () => simModal.showModal());
  document.getElementById("btn-close-simulate").addEventListener("click", () => simModal.close());
  document.getElementById("btn-cancel-simulate").addEventListener("click", () => simModal.close());

  // Preset Scenario Buttons in Simulate Modal
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-preset");
      const p = PRESET_SCENARIOS[key];
      if (p) {
        document.getElementById("sim-name").value = p.name;
        document.getElementById("sim-email").value = p.email;
        document.getElementById("sim-company").value = p.company;
        document.getElementById("sim-tier").value = p.tier;
        document.getElementById("sim-subject").value = p.subject;
        document.getElementById("sim-message").value = p.message;
      }
    });
  });

  document.getElementById("form-simulate-ticket").addEventListener("submit", handleSimulateTicket);

  // Modal: Escalate
  const escModal = document.getElementById("modal-escalate");
  document.getElementById("btn-escalate-modal").addEventListener("click", () => escModal.showModal());
  document.getElementById("btn-close-escalate").addEventListener("click", () => escModal.close());
  document.getElementById("btn-cancel-escalate").addEventListener("click", () => escModal.close());
  document.getElementById("form-escalate").addEventListener("submit", handleEscalateTicket);

  // Modal: Analytics
  const analyticsModal = document.getElementById("modal-analytics");
  document.getElementById("btn-analytics").addEventListener("click", () => {
    renderAnalyticsModal();
    analyticsModal.showModal();
  });
  document.getElementById("btn-close-analytics").addEventListener("click", () => analyticsModal.close());

  // Universal backdrop click to close dialogs
  [simModal, escModal, analyticsModal].forEach(dialog => {
    if (!dialog) return;
    dialog.addEventListener("click", (e) => {
      const rect = dialog.getBoundingClientRect();
      const clickedInside = (
        rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
        rect.left <= e.clientX && e.clientX <= rect.left + rect.width
      );
      if (!clickedInside) {
        dialog.close();
      }
    });
  });
}

async function handleSendResolution() {
  if (!state.selectedTicketId) return;
  const finalBody = document.getElementById("reply-textarea").value;
  try {
    const res = await fetch(`/api/tickets/${state.selectedTicketId}/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ finalBody })
    });
    if (res.ok) {
      showToast(`Reply dispatched to customer! Ticket marked as Resolved.`, "success");
      await loadStats();
      await loadTickets();
    }
  } catch (err) {
    showToast("Failed to dispatch reply.", "info");
  }
}

async function handleRegenerateDraft() {
  if (!state.selectedTicketId) return;
  const tone = document.getElementById("tone-select").value;
  showToast(`Regenerating draft with ${tone} tone via Knowledge Brain...`, "info");
  try {
    const res = await fetch(`/api/tickets/${state.selectedTicketId}/draft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tone })
    });
    if (res.ok) {
      const updated = await res.json();
      const idx = state.tickets.findIndex(t => t.id === updated.id);
      if (idx !== -1) state.tickets[idx] = updated;
      renderTicketDetail();
      showToast("Draft updated with fresh Knowledge Brain citations!", "success");
    }
  } catch (err) {
    showToast("Failed to regenerate draft.", "info");
  }
}

async function handleSimulateTicket(e) {
  e.preventDefault();
  const payload = {
    customer: {
      name: document.getElementById("sim-name").value,
      email: document.getElementById("sim-email").value,
      company: document.getElementById("sim-company").value,
      tier: document.getElementById("sim-tier").value
    },
    subject: document.getElementById("sim-subject").value,
    message: document.getElementById("sim-message").value
  };

  try {
    const res = await fetch("/api/tickets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const created = await res.json();
      document.getElementById("modal-simulate").close();
      showToast(`New inquiry ${created.id} received & auto-drafted!`, "success");
      await loadStats();
      await loadTickets();
      selectTicket(created.id);
    }
  } catch (err) {
    showToast("Failed to simulate ticket.", "info");
  }
}

async function handleEscalateTicket(e) {
  e.preventDefault();
  if (!state.selectedTicketId) return;

  const payload = {
    reason: document.getElementById("esc-reason").value,
    note: document.getElementById("esc-note").value
  };

  try {
    const res = await fetch(`/api/tickets/${state.selectedTicketId}/escalate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      document.getElementById("modal-escalate").close();
      showToast(`Ticket ${state.selectedTicketId} escalated to Platform Engineering!`, "info");
      await loadStats();
      await loadTickets();
    }
  } catch (err) {
    showToast("Failed to escalate ticket.", "info");
  }
}

function renderAnalyticsModal() {
  document.getElementById("stat-deflection").textContent = `${state.stats.deflectionRate || 78}%`;
  const categoriesBox = document.getElementById("analytics-categories");
  const cats = state.stats.categories || {};
  const total = state.stats.total || 1;

  categoriesBox.innerHTML = Object.entries(cats).map(([cat, count]) => {
    const pct = Math.round((count / total) * 100);
    return `
      <div class="cat-bar-row">
        <span class="cat-bar-label">${escapeHtml(cat)}</span>
        <div class="cat-bar-track">
          <div class="cat-bar-fill" style="width: ${pct}%;"></div>
        </div>
        <span style="font-family:var(--font-mono); font-size:0.72rem; color:var(--text-dim);">${count} (${pct}%)</span>
      </div>`;
  }).join("");
}

// ─── Utilities ───────────────────────────────────────────────────────────────

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function formatStatusLabel(status) {
  return {
    needs_review: "Needs Review",
    auto_drafted: "Auto-Drafted",
    escalated: "Escalated to Human",
    resolved: "Resolved"
  }[status] || status;
}

function getStatusBadgeClass(status) {
  return {
    needs_review: "badge-amber",
    auto_drafted: "badge-indigo",
    escalated: "badge-rose",
    resolved: "badge-emerald"
  }[status] || "badge-outline";
}

function formatTimeAgo(isoString) {
  if (!isoString) return "just now";
  const diffMs = Date.now() - new Date(isoString).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
