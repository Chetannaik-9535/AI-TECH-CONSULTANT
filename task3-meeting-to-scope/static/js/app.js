/**
 * AI Tech Consultant - Meeting to Scope Frontend Application
 * Handles discovery sessions, AI requirement extraction, and SOW compilation.
 */

const state = {
  meetings: [],
  selectedMeetingId: null,
  activeMeeting: null,
  activeAnalysis: null,
  activeSow: null,
  hourlyRate: 150
};

document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadMeetings();
});

// ─── API Operations ──────────────────────────────────────────────────────────

async function loadMeetings() {
  try {
    const res = await fetch("/api/meetings");
    if (res.ok) {
      state.meetings = await res.json();
      renderMeetingList();
      if (state.meetings.length > 0 && !state.selectedMeetingId) {
        selectMeeting(state.meetings[0].id);
      }
    }
  } catch (err) {
    console.error("Failed to load discovery meetings:", err);
  }
}

async function selectMeeting(meetingId) {
  state.selectedMeetingId = meetingId;
  state.activeAnalysis = null;
  state.activeSow = null;

  // Highlight selected card
  document.querySelectorAll(".meeting-card").forEach(c => {
    c.classList.toggle("selected", c.getAttribute("data-meeting-id") === meetingId);
  });

  try {
    const res = await fetch(`/api/meetings/${meetingId}`);
    if (res.ok) {
      state.activeMeeting = await res.json();
      renderMeetingHeader();
      renderTranscriptDialogue();
      resetAnalysisView();
      resetSowView();
    }
  } catch (err) {
    console.error("Failed to fetch meeting details:", err);
  }
}

async function triggerAnalysis() {
  if (!state.selectedMeetingId) return;
  showToast("Extracting technical requirements with AI...", "info");

  try {
    const res = await fetch(`/api/meetings/${state.selectedMeetingId}/analyze`, {
      method: "POST"
    });
    if (res.ok) {
      state.activeAnalysis = await res.json();
      renderAnalysisView();
      switchTab("tab-analysis");
      showToast(`Extracted ${state.activeAnalysis.requirements.length} requirements!`, "success");
    }
  } catch (err) {
    showToast("Failed to run requirement extraction.", "info");
  }
}

async function triggerGenerateSow() {
  if (!state.selectedMeetingId) return;
  showToast("Compiling executive Scope of Work (SOW)...", "info");

  try {
    const res = await fetch(`/api/meetings/${state.selectedMeetingId}/generate-sow?hourly_rate=${state.hourlyRate}`, {
      method: "POST"
    });
    if (res.ok) {
      state.activeSow = await res.json();
      renderSowView();
      showToast("Scope of Work document generated!", "success");
    }
  } catch (err) {
    showToast("Failed to generate SOW.", "info");
  }
}

// ─── Rendering Methods ───────────────────────────────────────────────────────

function renderMeetingList() {
  const container = document.getElementById("meetings-list-container");
  const countBadge = document.getElementById("meeting-count-badge");
  countBadge.textContent = state.meetings.length;

  container.innerHTML = state.meetings.map(m => {
    const isSel = m.id === state.selectedMeetingId;
    return `
      <div class="meeting-card ${isSel ? 'selected' : ''}" data-meeting-id="${m.id}">
        <div class="meeting-card-top">
          <span>${m.id}</span>
          <span>${m.duration_minutes}m</span>
        </div>
        <h4 class="meeting-card-title">${escapeHtml(m.title)}</h4>
        <div class="meeting-card-client">${escapeHtml(m.client_name)} &bull; ${escapeHtml(m.client_company)}</div>
      </div>`;
  }).join("");

  container.querySelectorAll(".meeting-card").forEach(card => {
    card.addEventListener("click", () => {
      selectMeeting(card.getAttribute("data-meeting-id"));
    });
  });
}

function renderMeetingHeader() {
  const m = state.activeMeeting;
  if (!m) return;
  document.getElementById("hdr-meeting-id").textContent = m.metadata.id;
  document.getElementById("hdr-meeting-date").textContent = m.metadata.date;
  document.getElementById("hdr-meeting-duration").textContent = `${m.metadata.duration_minutes} mins`;
  document.getElementById("hdr-meeting-title").textContent = m.metadata.title;

  const partsContainer = document.getElementById("hdr-participants-list");
  partsContainer.innerHTML = (m.metadata.participants || []).map(p => `
    <span class="participant-pill">${escapeHtml(p)}</span>
  `).join("");
}

function renderTranscriptDialogue() {
  const container = document.getElementById("transcript-dialogue-container");
  const text = state.activeMeeting?.transcript || "";
  const lines = text.split("\n").filter(l => l.trim().length > 0);

  container.innerHTML = lines.map(line => {
    const match = line.match(/^\[([0-9:]+)\]\s*([^:]+):\s*(.*)$/);
    if (match) {
      const time = match[1];
      const speaker = match[2];
      const content = match[3];
      const isConsultant = speaker.toLowerCase().includes("jordan") || speaker.toLowerCase().includes("consultant");

      return `
        <div class="utterance-row ${isConsultant ? 'consultant' : ''}">
          <div class="utterance-time">${time}</div>
          <div class="utterance-content">
            <div class="utterance-speaker">${escapeHtml(speaker)}</div>
            <div>${escapeHtml(content)}</div>
          </div>
        </div>`;
    }

    return `
      <div class="utterance-row">
        <div class="utterance-content">${escapeHtml(line)}</div>
      </div>`;
  }).join("");
}

function renderAnalysisView() {
  const a = state.activeAnalysis;
  const container = document.getElementById("analysis-results-view");
  if (!a) return;

  const reqBadge = document.getElementById("req-count-badge");
  reqBadge.style.display = "inline-block";
  reqBadge.textContent = a.requirements.length;

  container.innerHTML = `
    <!-- Executive Overview Card -->
    <div class="analysis-card">
      <h4>🎯 Strategic Discovery Overview</h4>
      <div class="meta-grid">
        <div class="meta-item full-width">
          <label>Executive Summary</label>
          <p>${escapeHtml(a.executive_summary)}</p>
        </div>
        <div class="meta-item">
          <label>Business &amp; Monetization Model</label>
          <p>${escapeHtml(a.business_model)}</p>
        </div>
        <div class="meta-item">
          <label>Target Audience</label>
          <p>${escapeHtml(a.target_audience)}</p>
        </div>
        <div class="meta-item">
          <label>Requested Timeline</label>
          <p>${escapeHtml(a.timeline_requested)}</p>
        </div>
      </div>
    </div>

    <!-- Requirements Table Card -->
    <div class="analysis-card">
      <h4>📋 Technical &amp; Functional Requirements (${a.requirements.length})</h4>
      <table class="requirements-table">
        <thead>
          <tr>
            <th>Ref</th>
            <th>Requirement Details</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Effort</th>
          </tr>
        </thead>
        <tbody>
          ${a.requirements.map(r => `
            <tr>
              <td><code>${r.id}</code></td>
              <td>
                <strong>${escapeHtml(r.title)}</strong>
                <p style="color:var(--text-muted); margin-top:3px;">${escapeHtml(r.description)}</p>
                ${r.recommended_bd_addon ? `<span class="addon-pill">⚡ ${escapeHtml(r.recommended_bd_addon)}</span>` : ''}
              </td>
              <td><span style="color:var(--text-muted);">${escapeHtml(r.category)}</span></td>
              <td><span class="req-badge ${getPriorityClass(r.priority)}">${r.priority}</span></td>
              <td style="font-family:var(--font-mono); color:var(--accent-cyan);">${r.estimated_hours}h</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>

    <!-- Out of Scope & Technical Risks -->
    <div class="analysis-card">
      <h4>🚫 Out of Scope Boundaries (Phase 1 Exclusions)</h4>
      <ul style="padding-left: 20px; font-size: 0.8rem; color: var(--text-muted); line-height: 1.6;">
        ${(a.out_of_scope || []).map(item => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>

    <div class="analysis-card">
      <h4>⚠️ Technical Feasibility &amp; Risk Mitigation</h4>
      <div style="display:flex; flex-direction:column; gap:10px;">
        ${(a.technical_risks || []).map(rk => `
          <div style="background:rgba(0,0,0,0.25); border:1px solid var(--border-subtle); padding:10px 12px; border-radius:var(--radius-md);">
            <div style="font-weight:700; color:#fca5a5; font-size:0.8rem; margin-bottom:2px;">🚨 ${escapeHtml(rk.risk)}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Impact: ${escapeHtml(rk.impact)}</div>
            <div style="font-size:0.75rem; color:#6ee7b7; margin-top:3px;">Mitigation: ${escapeHtml(rk.mitigation)}</div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function renderSowView() {
  const sow = state.activeSow;
  if (!sow) return;

  document.getElementById("empty-sow").style.display = "none";
  document.getElementById("sow-rendered-wrapper").style.display = "block";

  // KPIs
  document.getElementById("kpi-hours").textContent = `${sow.total_hours} hrs`;
  document.getElementById("kpi-rate").textContent = `$${sow.hourly_rate}/hr`;
  document.getElementById("kpi-cost").textContent = `$${sow.total_cost.toLocaleString()}`;
  document.getElementById("kpi-weeks").textContent = `${sow.timeline_weeks} wks`;

  // Phases Accordion
  const phasesContainer = document.getElementById("sow-phases-list");
  phasesContainer.innerHTML = sow.phases.map((p, idx) => `
    <div class="phase-card ${idx === 0 ? 'expanded' : ''}" data-phase-idx="${idx}">
      <div class="phase-card-header" style="cursor: pointer; user-select: none;" title="Click to toggle phase deliverables">
        <div style="display:flex; align-items:center; gap:8px;">
          <span class="phase-toggle-icon" style="font-size:0.75rem; color:var(--accent-indigo); transition:transform 0.2s ease;">${idx === 0 ? '▼' : '▶'}</span>
          <span class="phase-title-text">${escapeHtml(p.phase_name)}</span>
        </div>
        <span class="phase-meta-numbers">${p.phase_hours} hrs &bull; $${p.phase_cost.toLocaleString()}</span>
      </div>
      <div class="phase-deliverables-list" style="display: ${idx === 0 ? 'block' : 'none'};">
        ${p.deliverables.map(d => `
          <div class="deliv-item">
            <div class="deliv-info">
              <strong>[${d.id}] ${escapeHtml(d.title)}</strong>
              <p>${escapeHtml(d.description)}</p>
            </div>
            <span class="deliv-hours">${d.estimated_hours}h</span>
          </div>
        `).join("")}
      </div>
    </div>
  `).join("");

  // Attach accordion click listeners
  phasesContainer.querySelectorAll(".phase-card-header").forEach(header => {
    header.addEventListener("click", () => {
      const card = header.closest(".phase-card");
      const list = card.querySelector(".phase-deliverables-list");
      const icon = card.querySelector(".phase-toggle-icon");
      const isHidden = list.style.display === "none";
      list.style.display = isHidden ? "block" : "none";
      if (icon) icon.textContent = isHidden ? "▼" : "▶";
      card.classList.toggle("expanded", isHidden);
    });
  });

  // Milestones
  const milestonesContainer = document.getElementById("milestones-table-container");
  milestonesContainer.innerHTML = `
    <table class="requirements-table">
      <thead>
        <tr>
          <th>Milestone</th>
          <th>Target</th>
          <th>Summary</th>
          <th>Payment</th>
        </tr>
      </thead>
      <tbody>
        ${sow.milestones.map(m => {
          const amt = Math.round((m.payment_percentage / 100) * sow.total_cost);
          return `
            <tr>
              <td><strong>${escapeHtml(m.name)}</strong></td>
              <td>Week ${m.target_week}</td>
              <td style="color:var(--text-muted);">${escapeHtml(m.deliverable_summary)}</td>
              <td style="font-family:var(--font-mono); color:var(--accent-emerald);">${m.payment_percentage}% ($${amt.toLocaleString()})</td>
            </tr>`;
        }).join("")}
      </tbody>
    </table>
  `;

  // Markdown rendering
  document.getElementById("sow-markdown-raw").value = sow.markdown_document;
  document.getElementById("sow-markdown-preview").innerHTML = renderBasicMarkdown(sow.markdown_document);
}

function resetAnalysisView() {
  document.getElementById("analysis-results-view").innerHTML = `
    <div class="empty-analysis-state">
      <p>Click <strong>"Extract Requirements"</strong> above to analyze this transcript using AI.</p>
    </div>`;
  document.getElementById("req-count-badge").style.display = "none";
}

function resetSowView() {
  document.getElementById("empty-sow").style.display = "block";
  document.getElementById("sow-rendered-wrapper").style.display = "none";
  document.getElementById("kpi-hours").textContent = "0 hrs";
  document.getElementById("kpi-cost").textContent = "$0";
  document.getElementById("kpi-weeks").textContent = "0 wks";
}

// ─── Event Listeners ─────────────────────────────────────────────────────────

function initEventListeners() {
  // Tab Switcher
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      switchTab(targetId);
    });
  });

  // Action Buttons
  document.getElementById("btn-run-analysis").addEventListener("click", triggerAnalysis);
  document.getElementById("btn-generate-sow").addEventListener("click", triggerGenerateSow);

  // Global Hourly Rate Input with debounce on typing
  const rateInput = document.getElementById("global-rate-input");
  let rateDebounce = null;
  const updateRate = (e) => {
    const val = parseFloat(e.target.value);
    if (!isNaN(val) && val > 0 && val !== state.hourlyRate) {
      state.hourlyRate = val;
      showToast(`Consultant rate set to $${val}/hr`, "info");
      if (state.activeSow) {
        triggerGenerateSow(); // recalculate SOW with new rate
      }
    }
  };
  rateInput.addEventListener("change", updateRate);
  rateInput.addEventListener("input", (e) => {
    clearTimeout(rateDebounce);
    rateDebounce = setTimeout(() => updateRate(e), 500);
  });

  // Copy Markdown
  document.getElementById("btn-copy-md").addEventListener("click", () => {
    if (!state.activeSow) {
      showToast("Generate an SOW document first.", "info");
      return;
    }
    navigator.clipboard.writeText(state.activeSow.markdown_document);
    showToast("Scope of Work Markdown copied to clipboard!", "success");
  });

  // Download Markdown
  document.getElementById("btn-download-md").addEventListener("click", () => {
    if (!state.activeSow) {
      showToast("Generate an SOW document first.", "info");
      return;
    }
    const blob = new Blob([state.activeSow.markdown_document], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${state.activeSow.sow_id}.md`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("Downloaded SOW markdown file!", "success");
  });

  // Toggle Raw Markdown View
  const toggleBtn = document.getElementById("btn-toggle-raw");
  toggleBtn.addEventListener("click", () => {
    const preview = document.getElementById("sow-markdown-preview");
    const raw = document.getElementById("sow-markdown-raw");
    const isRaw = raw.style.display === "block";
    raw.style.display = isRaw ? "none" : "block";
    preview.style.display = isRaw ? "block" : "none";
    toggleBtn.textContent = isRaw ? "Toggle Raw Markdown" : "View Formatted";
  });

  // Ingest Modal
  const modal = document.getElementById("modal-ingest");
  document.getElementById("btn-new-meeting").addEventListener("click", () => {
    document.getElementById("inp-date").value = new Date().toISOString().split("T")[0];
    modal.showModal();
  });
  document.getElementById("btn-close-ingest").addEventListener("click", () => modal.close());
  document.getElementById("btn-cancel-ingest").addEventListener("click", () => modal.close());

  // Backdrop click to close ingest modal
  modal.addEventListener("click", (e) => {
    const rect = modal.getBoundingClientRect();
    const clickedInside = (
      rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX && e.clientX <= rect.left + rect.width
    );
    if (!clickedInside) {
      modal.close();
    }
  });

  document.getElementById("form-ingest-meeting").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      metadata: {
        id: "",
        title: document.getElementById("inp-title").value,
        client_name: document.getElementById("inp-client-name").value,
        client_company: document.getElementById("inp-company").value,
        date: document.getElementById("inp-date").value,
        duration_minutes: 45,
        participants: document.getElementById("inp-participants").value.split(",").map(s => s.trim()).filter(Boolean)
      },
      transcript: document.getElementById("inp-transcript").value,
      custom_notes: document.getElementById("inp-notes").value
    };

    try {
      const res = await fetch("/api/meetings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const created = await res.json();
        modal.close();
        showToast("New meeting transcript ingested!", "success");
        await loadMeetings();
        selectMeeting(created.metadata.id);
      }
    } catch (err) {
      showToast("Failed to save transcript.", "info");
    }
  });

  // Meeting Search
  document.getElementById("meeting-search-input").addEventListener("input", (e) => {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll(".meeting-card").forEach(c => {
      const txt = c.textContent.toLowerCase();
      c.style.display = txt.includes(query) ? "flex" : "none";
    });
  });
}

function switchTab(tabId) {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabId);
  });
  document.querySelectorAll(".tab-view").forEach(view => {
    view.classList.toggle("active", view.id === tabId);
  });
}

// ─── Utilities ───────────────────────────────────────────────────────────────

function getPriorityClass(priority) {
  if (priority === "Must Have") return "req-must";
  if (priority === "Should Have") return "req-should";
  return "req-nice";
}

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

function renderBasicMarkdown(md) {
  if (!md) return "";
  return md
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/\n$/gim, '<br />')
    .replace(/^\- (.*$)/gim, '<li>$1</li>');
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
