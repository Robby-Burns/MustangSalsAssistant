class DemoPageBuilder:
    @staticmethod
    def render() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mustang Sage Teams Demo</title>
  <style>
    :root {
      --teams-bg: #f5f6fa;
      --teams-shell: #eef1f6;
      --teams-panel: #ffffff;
      --teams-border: #d7dce8;
      --teams-text: #242424;
      --teams-muted: #616161;
      --teams-primary: #6264a7;
      --teams-primary-dark: #4f52b2;
      --teams-primary-soft: rgba(98, 100, 167, 0.10);
      --teams-green: #107c10;
      --teams-amber: #c19c00;
      --teams-red: #c4314b;
      --teams-shadow: 0 18px 40px rgba(36, 36, 36, 0.10);
      --font: "Segoe UI", Tahoma, sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: var(--font);
      color: var(--teams-text);
      background: linear-gradient(180deg, #f9fafc 0%, var(--teams-bg) 100%);
    }

    .teams-shell {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 72px 300px minmax(620px, 1fr) 520px;
      background: var(--teams-shell);
    }

    .app-rail {
      background: linear-gradient(180deg, #4d4f93 0%, #6264a7 100%);
      color: #fff;
      padding: 18px 12px;
      display: grid;
      grid-template-rows: auto auto 1fr auto;
      gap: 18px;
      align-items: start;
    }

    .rail-badge,
    .rail-icon {
      width: 48px;
      height: 48px;
      border-radius: 16px;
      display: grid;
      place-items: center;
      background: rgba(255, 255, 255, 0.14);
      border: 1px solid rgba(255, 255, 255, 0.12);
      font-weight: 700;
      margin: 0 auto;
    }

    .rail-stack {
      display: grid;
      gap: 12px;
    }

    .queue-pane,
    .chat-pane,
    .detail-pane {
      display: grid;
      grid-template-rows: auto 1fr;
      min-width: 0;
      background: var(--teams-panel);
      border-left: 1px solid var(--teams-border);
    }

    .pane-header {
      padding: 18px 20px;
      border-bottom: 1px solid var(--teams-border);
      background: linear-gradient(180deg, #fff 0%, #f7f8fb 100%);
    }

    .pane-header h1,
    .pane-header h2,
    .pane-header h3 {
      margin: 0;
      font-size: 1rem;
      font-weight: 700;
    }

    .pane-header p {
      margin: 6px 0 0;
      color: var(--teams-muted);
      font-size: 0.92rem;
      line-height: 1.45;
    }

    .queue-body {
      padding: 16px;
      overflow: auto;
      display: grid;
      gap: 16px;
      align-content: start;
      background: #fafbfe;
    }

    .quick-create,
    .queue-card {
      background: #fff;
      border: 1px solid var(--teams-border);
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 8px 20px rgba(36, 36, 36, 0.05);
    }

    .queue-list {
      display: grid;
      gap: 10px;
    }

    .queue-item {
      width: 100%;
      text-align: left;
      border: 1px solid var(--teams-border);
      background: #fff;
      border-radius: 14px;
      padding: 12px;
      cursor: pointer;
      font: inherit;
      transition: background 120ms ease, transform 120ms ease;
    }

    .queue-item:hover,
    .toolbar-button:hover,
    .action-button:hover,
    .mini-button:hover {
      transform: translateY(-1px);
    }

    .queue-item.active {
      border-color: var(--teams-primary);
      background: var(--teams-primary-soft);
    }

    .queue-item strong,
    .queue-item span {
      display: block;
    }

    .queue-item span {
      margin-top: 4px;
      color: var(--teams-muted);
      font-size: 0.9rem;
    }

    .queue-item .badge-row {
      margin-top: 10px;
    }

    .chat-header {
      padding: 14px 20px;
      border-bottom: 1px solid var(--teams-border);
      background: #fff;
      display: grid;
      gap: 12px;
    }

    .chat-title {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }

    .chat-title h2 {
      margin: 0;
      font-size: 1.06rem;
    }

    .badge {
      display: inline-flex;
      gap: 8px;
      align-items: center;
      border-radius: 999px;
      padding: 7px 11px;
      font-size: 0.83rem;
      border: 1px solid var(--teams-border);
      background: #f6f7fb;
      color: var(--teams-muted);
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .toolbar-button,
    .action-button,
    .mini-button {
      appearance: none;
      border: 1px solid var(--teams-border);
      background: #fff;
      border-radius: 10px;
      padding: 10px 14px;
      font: inherit;
      cursor: pointer;
      transition: background 120ms ease, transform 120ms ease;
    }

    .toolbar-button.primary,
    .action-button.primary,
    .mini-button.primary {
      background: var(--teams-primary);
      border-color: var(--teams-primary);
      color: #fff;
    }

    .toolbar-button.subtle,
    .mini-button.subtle {
      background: #f8f9fd;
    }

    .chat-body {
      display: grid;
      grid-template-rows: 1fr auto;
      min-height: 0;
      background:
        radial-gradient(circle at top right, rgba(98, 100, 167, 0.10), transparent 28%),
        linear-gradient(180deg, #f7f8fc 0%, #eef1f6 100%);
    }

    .timeline {
      padding: 18px 20px;
      overflow: auto;
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .message {
      max-width: min(100%, 1200px);
      border-radius: 16px;
      padding: 14px 16px;
      border: 1px solid var(--teams-border);
      background: #fff;
      box-shadow: 0 10px 24px rgba(36, 36, 36, 0.08);
    }

    .message.rep {
      margin-left: auto;
      width: min(70%, 720px);
      background: linear-gradient(180deg, #6264a7 0%, #5457a3 100%);
      color: #fff;
      border-color: rgba(98, 100, 167, 0.45);
    }

    .message-meta {
      font-size: 0.77rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      color: var(--teams-muted);
      margin-bottom: 6px;
    }

    .message.rep .message-meta {
      color: rgba(255, 255, 255, 0.86);
    }

    .message-text {
      line-height: 1.5;
      white-space: pre-wrap;
    }

    .quote-card,
    .email-card,
    .notice-card {
      margin-top: 12px;
      width: min(100%, 1220px);
      border-radius: 18px;
      overflow: hidden;
      border: 1px solid var(--teams-border);
      background: #fff;
      box-shadow: var(--teams-shadow);
    }

    .card-hero {
      padding: 18px 20px;
      background: linear-gradient(135deg, #6264a7 0%, #7a7dd8 100%);
      color: #fff;
    }

    .card-hero h3 {
      margin: 0;
      font-size: 1.12rem;
    }

    .card-hero p {
      margin: 6px 0 0;
      color: rgba(255, 255, 255, 0.88);
    }

    .card-grid {
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.95fr);
      gap: 0;
    }

    .card-section {
      padding: 18px 20px;
      display: grid;
      gap: 12px;
      align-content: start;
      border-right: 1px solid var(--teams-border);
    }

    .card-section:last-child {
      border-right: 0;
      background: #fbfbfe;
    }

    .section-title {
      font-size: 0.78rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--teams-muted);
      font-weight: 700;
    }

    .fact-grid,
    .line-items,
    .compliance-list,
    .source-list,
    .event-list {
      display: grid;
      gap: 10px;
    }

    .fact-row,
    .line-row,
    .compliance-row,
    .source-row,
    .event-row {
      display: grid;
      gap: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid #eceef5;
    }

    .fact-row {
      grid-template-columns: 210px 1fr;
    }

    .line-row {
      grid-template-columns: 1.4fr 100px 120px 110px;
      align-items: center;
    }

    .compliance-row {
      grid-template-columns: 1fr auto;
      align-items: start;
    }

    .source-row,
    .event-row {
      grid-template-columns: 1fr auto;
      align-items: start;
    }

    .fact-row:last-child,
    .line-row:last-child,
    .compliance-row:last-child,
    .source-row:last-child,
    .event-row:last-child {
      border-bottom: 0;
      padding-bottom: 0;
    }

    .fact-label,
    .line-header,
    .muted {
      color: var(--teams-muted);
    }

    .source-badges {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 8px;
    }

    .source-tag {
      display: inline-flex;
      gap: 6px;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.78rem;
      background: #f4f6fb;
      border: 1px solid var(--teams-border);
    }

    .source-tag.retrieved { color: var(--teams-green); }
    .source-tag.inferred { color: var(--teams-primary); }
    .source-tag.user { color: var(--teams-amber); }

    .composer {
      padding: 16px 20px;
      border-top: 1px solid var(--teams-border);
      background: #fff;
      display: grid;
      gap: 12px;
    }

    .composer textarea,
    .field input,
    .field select,
    .field textarea,
    .line-cell input,
    .line-cell textarea {
      width: 100%;
      border: 1px solid var(--teams-border);
      border-radius: 10px;
      padding: 10px 12px;
      font: inherit;
      color: var(--teams-text);
      background: #fff;
    }

    .composer textarea,
    .field textarea {
      min-height: 88px;
      resize: vertical;
    }

    .detail-body {
      overflow: auto;
      background: #fbfcfe;
      padding: 16px;
      display: grid;
      gap: 14px;
      align-content: start;
    }

    .tabs {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 4px;
    }

    .tab {
      text-align: center;
      padding: 10px 8px;
      border-radius: 10px;
      border: 1px solid var(--teams-border);
      cursor: pointer;
      background: #fff;
      font-size: 0.9rem;
    }

    .tab.active {
      background: var(--teams-primary-soft);
      border-color: var(--teams-primary);
      color: var(--teams-primary-dark);
      font-weight: 700;
    }

    .detail-section {
      display: none;
      background: #fff;
      border: 1px solid var(--teams-border);
      border-radius: 16px;
      padding: 16px;
      gap: 14px;
      box-shadow: 0 8px 20px rgba(36, 36, 36, 0.04);
    }

    .detail-section.active {
      display: grid;
    }

    .field-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }

    .field-grid.single {
      grid-template-columns: 1fr;
    }

    .field {
      display: grid;
      gap: 6px;
      font-size: 0.9rem;
      color: var(--teams-muted);
    }

    .field.full {
      grid-column: 1 / -1;
    }

    .section-actions,
    .card-actions,
    .line-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }

    .line-edit-table {
      display: grid;
      gap: 10px;
    }

    .line-edit-row {
      display: grid;
      grid-template-columns: 1.25fr 90px 110px 1fr auto;
      gap: 8px;
      align-items: start;
    }

    .status-pill {
      display: inline-flex;
      padding: 5px 10px;
      border-radius: 999px;
      font-size: 0.76rem;
      border: 1px solid var(--teams-border);
      background: #f5f6fa;
    }

    .status-pill.ok { color: var(--teams-green); }
    .status-pill.review { color: var(--teams-red); }
    .status-pill.draft { color: var(--teams-primary-dark); }

    .mini-label {
      font-size: 0.78rem;
      color: var(--teams-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-weight: 700;
    }

    .empty-state {
      padding: 16px;
      border-radius: 14px;
      background: #f7f8fc;
      border: 1px dashed var(--teams-border);
      color: var(--teams-muted);
      line-height: 1.5;
    }

    details.debug-box {
      border: 1px solid var(--teams-border);
      border-radius: 12px;
      background: #fff;
      overflow: hidden;
    }

    details.debug-box summary {
      padding: 12px 14px;
      cursor: pointer;
      font-weight: 700;
      background: #f8f9fd;
    }

    details.debug-box pre {
      margin: 0;
      padding: 14px;
      overflow: auto;
      font-size: 0.82rem;
      background: #fff;
    }

    @media (max-width: 1680px) {
      .teams-shell {
        grid-template-columns: 72px 280px minmax(560px, 1fr) 460px;
      }
    }

    @media (max-width: 1380px) {
      .teams-shell {
        grid-template-columns: 72px 260px 1fr;
      }

      .detail-pane {
        grid-column: 2 / -1;
        border-top: 1px solid var(--teams-border);
      }
    }

    @media (max-width: 980px) {
      .teams-shell {
        grid-template-columns: 1fr;
      }

      .app-rail {
        grid-template-columns: repeat(4, auto);
        grid-template-rows: none;
        justify-content: center;
      }

      .queue-pane,
      .chat-pane,
      .detail-pane {
        border-left: 0;
        border-top: 1px solid var(--teams-border);
      }

      .card-grid,
      .field-grid,
      .line-edit-row,
      .line-row,
      .fact-row {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="teams-shell">
    <aside class="app-rail">
      <div class="rail-badge">MS</div>
      <div class="rail-stack">
        <div class="rail-icon">C</div>
        <div class="rail-icon">Q</div>
        <div class="rail-icon">@</div>
      </div>
      <div></div>
      <div class="rail-icon">...</div>
    </aside>

    <aside class="queue-pane">
      <div class="pane-header">
        <h1>Mustang Sage</h1>
        <p>Sales quoting workspace styled as a Teams conversation with live retrieved context and editable draft state.</p>
      </div>
      <div class="queue-body">
        <section class="quick-create">
          <div class="mini-label">Start From Lead</div>
          <div class="field-grid single" style="margin-top:10px;">
            <label class="field">
              Lead ID
              <input id="newLeadId" type="text" value="LD-123" />
            </label>
            <label class="field">
              Request Notes
              <textarea id="newLeadNotes" placeholder="Customer needs a double-sided illuminated monument sign with updated address details."></textarea>
            </label>
          </div>
          <div class="section-actions" style="margin-top:12px;">
            <button class="toolbar-button primary" onclick="createOrSwitchSession()">Open Workspace</button>
            <button class="toolbar-button subtle" onclick="seedBlankOpportunity()">New Opportunity</button>
          </div>
        </section>

        <section class="queue-card">
          <div class="mini-label">Active Queue</div>
          <div class="queue-list" id="queueList" style="margin-top:12px;"></div>
        </section>

        <section class="queue-card">
          <div class="mini-label">Source Provenance</div>
          <div class="source-list" id="sourceContext" style="margin-top:12px;"></div>
        </section>
      </div>
    </aside>

    <main class="chat-pane">
      <div class="chat-header">
        <div class="chat-title">
          <h2 id="conversationTitle">Quote Review</h2>
          <div class="badge" id="statusBadge">No session</div>
        </div>
        <div class="toolbar">
          <button class="toolbar-button primary" onclick="runQuote()">Run Quote</button>
          <button class="toolbar-button" onclick="saveLead()">Save Lead</button>
          <button class="toolbar-button" onclick="regenerateQuote()">Manual Regenerate</button>
          <button class="toolbar-button" onclick="prepareEmail()">Prepare Email</button>
          <button class="toolbar-button" onclick="toggleDebug()">Toggle Debug</button>
        </div>
      </div>

      <div class="chat-body">
        <div class="timeline" id="timeline"></div>
        <div class="composer">
          <div class="mini-label">Rep Request Notes</div>
          <textarea id="repNote" placeholder="Example: Keep monument footprint under city limits, switch to Richland site, add customer logo panel, and tighten timeline."></textarea>
          <div class="section-actions">
            <button class="toolbar-button" onclick="appendRepNote()">Add Note To Thread</button>
            <button class="toolbar-button" onclick="requestChanges()">Request Changes</button>
            <button class="toolbar-button" onclick="approveQuote()">Approve Quote</button>
            <button class="toolbar-button" onclick="dismissCard()">Dismiss Current Card</button>
          </div>
        </div>
      </div>
    </main>

    <aside class="detail-pane">
      <div class="pane-header">
        <h3>Quote Workspace</h3>
        <p>Editable lead context, line items, pricing, code review, and customer email draft.</p>
      </div>
      <div class="detail-body">
        <div class="tabs">
          <button class="tab active" data-tab="details" onclick="showTab('details')">Details</button>
          <button class="tab" data-tab="quote" onclick="showTab('quote')">Quote</button>
          <button class="tab" data-tab="codes" onclick="showTab('codes')">Codes</button>
          <button class="tab" data-tab="email" onclick="showTab('email')">Email</button>
        </div>

        <section class="detail-section active" id="tab-details">
          <div class="mini-label">Lead Intake</div>
          <div class="field-grid">
            <label class="field">
              Lead ID
              <input id="leadId" type="text" />
            </label>
            <label class="field">
              Pipeline Stage
              <input id="pipelineStage" type="text" />
            </label>
            <label class="field">
              Company
              <input id="company" type="text" />
            </label>
            <label class="field">
              Contact Name
              <input id="contactName" type="text" />
            </label>
            <label class="field">
              Project Type
              <select id="projectType">
                <option>Monument Sign</option>
                <option>Pylon Sign</option>
                <option>Channel Letters</option>
              </select>
            </label>
            <label class="field">
              Last Activity
              <input id="lastActivity" type="text" />
            </label>
            <label class="field full">
              Site Address
              <input id="addressInput" type="text" />
            </label>
            <label class="field full">
              Open Notes
              <textarea id="openNotes"></textarea>
            </label>
          </div>
          <div class="source-badges" id="detailFieldSources"></div>
          <div class="section-actions">
            <button class="toolbar-button primary" onclick="saveLead()">Save Lead Context</button>
          </div>
        </section>

        <section class="detail-section" id="tab-quote">
          <div class="mini-label">Quote Editor</div>
          <div class="field-grid">
            <label class="field">
              Quote ID
              <input id="quoteId" type="text" disabled />
            </label>
            <label class="field">
              Project Name
              <input id="projectName" type="text" />
            </label>
            <label class="field">
              Travel SKU
              <input id="travelSku" type="text" />
            </label>
            <label class="field">
              Travel Fee
              <input id="travelFee" type="number" step="0.01" />
            </label>
            <label class="field">
              Permit Fees
              <input id="permitFees" type="number" step="0.01" />
            </label>
            <label class="field">
              Gross Margin %
              <input id="grossMargin" type="number" step="0.01" />
            </label>
          </div>

          <div class="mini-label">Line Items</div>
          <div class="line-edit-table" id="lineItemEditor"></div>
          <div class="line-actions">
            <button class="mini-button" onclick="addLineItem()">Add Line Item</button>
            <button class="mini-button" onclick="saveQuote()">Save Quote Edits</button>
          </div>
        </section>

        <section class="detail-section" id="tab-codes">
          <div class="mini-label">Municipal Code Review</div>
          <div id="codeReviewEditor"></div>
          <div class="section-actions">
            <button class="toolbar-button primary" onclick="saveCodeReview()">Save Code Review</button>
          </div>
        </section>

        <section class="detail-section" id="tab-email">
          <div class="mini-label">Customer Email</div>
          <div class="field-grid single">
            <label class="field">
              Subject
              <input id="emailSubject" type="text" />
            </label>
            <label class="field">
              Body
              <textarea id="emailBody"></textarea>
            </label>
          </div>
          <div class="section-actions">
            <button class="toolbar-button" onclick="prepareEmail()">Generate Draft</button>
            <button class="toolbar-button" onclick="saveEmail()">Save Draft</button>
            <button class="toolbar-button primary" onclick="confirmSend()">Preview, Edit, Confirm Send</button>
          </div>
        </section>

        <section id="debugPanel" class="detail-section">
          <details class="debug-box" open>
            <summary>Raw Session</summary>
            <pre id="sessionDump">{}</pre>
          </details>
        </section>
      </div>
    </aside>
  </div>

  <script>
    let session = null;
    let debugVisible = false;
    let currentTab = "details";

    async function createOrSwitchSession(overrides = {}) {
      const leadId = document.getElementById("newLeadId").value.trim() || "LD-123";
      const requestNotes = document.getElementById("newLeadNotes").value.trim();
      const payload = {
        lead_id: leadId,
        overrides: Object.assign({
          Lead_ID: leadId,
          Open_Notes: requestNotes || "Demo workspace initialized.",
          Company: overrides.Company || undefined,
          Contact_Name: overrides.Contact_Name || undefined,
          Project_Type: overrides.Project_Type || undefined,
          Address_Input: overrides.Address_Input || undefined
        }, overrides)
      };
      const response = await fetch("/demo/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      session = await response.json();
      if (requestNotes) {
        await postAction("append_note", requestNotes);
      }
      renderSession();
    }

    function seedBlankOpportunity() {
      document.getElementById("newLeadId").value = "LD-NEW";
      document.getElementById("newLeadNotes").value = "New customer request started from scratch.";
      createOrSwitchSession({
        Company: "New Opportunity",
        Contact_Name: "Prospect",
        Project_Type: "Monument Sign",
        Address_Input: "123 Main St, Kennewick, WA"
      });
    }

    async function runQuote() {
      await ensureSession();
      const response = await fetch(`/demo/api/session/${session.session_id}/quote`, { method: "POST" });
      session = await response.json();
      renderSession();
      showTab("quote");
    }

    async function regenerateQuote() {
      await ensureSession();
      session = await postAction("regenerate_quote");
      renderSession();
      showTab("quote");
    }

    async function saveLead() {
      await ensureSession();
      const payload = {
        lead_context: {
          Lead_ID: value("leadId"),
          Pipeline_Stage: value("pipelineStage"),
          Company: value("company"),
          Contact_Name: value("contactName"),
          Project_Type: value("projectType"),
          Last_Activity_Date: value("lastActivity"),
          Address_Input: value("addressInput"),
          Open_Notes: value("openNotes")
        }
      };
      session = await postAction("save_lead", "", payload);
      renderSession();
      setStatus("Lead context saved");
    }

    async function saveQuote() {
      await ensureSession();
      const payload = {
        quote_draft: {
          Project_Name: value("projectName"),
          Travel_SKU: value("travelSku"),
          Travel_Fee_Amount: numberValue("travelFee"),
          Permit_Fees: numberValue("permitFees"),
          Gross_Margin_Pct: numberValue("grossMargin"),
          Line_Items: collectLineItems()
        }
      };
      session = await postAction("save_quote", "", payload);
      renderSession();
      setStatus("Quote edits saved");
    }

    async function saveCodeReview() {
      await ensureSession();
      const payload = { code_review: collectCodeReview() };
      session = await postAction("set_code_status", "", payload);
      renderSession();
      setStatus("Code review saved");
    }

    async function prepareEmail() {
      await ensureSession();
      if (!session.quote_draft || session.quote_draft.Status !== "approved_pending_submission") {
        setStatus("Approve the quote before preparing the email");
        return;
      }
      session = await postAction("trigger_nudge");
      renderSession();
      showTab("email");
    }

    async function saveEmail() {
      await ensureSession();
      const payload = {
        comm_draft: {
          Subject: value("emailSubject"),
          Body: value("emailBody")
        }
      };
      session = await postAction("save_email", "", payload);
      renderSession();
      setStatus("Email draft saved");
    }

    async function confirmSend() {
      await ensureSession();
      await saveEmail();
      session = await postAction("confirm_send");
      renderSession();
      showTab("email");
      setStatus("Email sent in demo mode");
    }

    async function appendRepNote() {
      await ensureSession();
      const note = value("repNote");
      if (!note) return;
      session = await postAction("append_note", note);
      document.getElementById("repNote").value = "";
      renderSession();
    }

    async function requestChanges() {
      await ensureSession();
      const note = value("repNote");
      session = await postAction("request_changes", note);
      renderSession();
      showTab("quote");
    }

    async function approveQuote() {
      await ensureSession();
      session = await postAction("approve_quote");
      renderSession();
      showTab("email");
      setStatus("Quote approved");
    }

    async function dismissCard() {
      await ensureSession();
      session = await postAction("dismiss");
      renderSession();
    }

    async function postAction(action, feedback = "", payload = {}) {
      const response = await fetch(`/demo/api/session/${session.session_id}/action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, feedback, payload })
      });
      return await response.json();
    }

    async function ensureSession() {
      if (!session) {
        await createOrSwitchSession();
      }
    }

    function renderSession() {
      if (!session) return;
      document.getElementById("conversationTitle").textContent =
        `${session.lead_context.Company || "Workspace"} | ${session.lead_context.Project_Type || "Quote"}`;
      document.getElementById("statusBadge").textContent =
        `${session.send_status || "draft"} | ${session.quote_draft ? session.quote_draft.Status : "no quote"}`;
      renderQueue();
      renderSourceContext();
      renderTimeline();
      hydrateLeadFields();
      hydrateQuoteFields();
      hydrateCodeReview();
      hydrateEmailDraft();
      renderFieldSources();
      document.getElementById("sessionDump").textContent = JSON.stringify(session, null, 2);
    }

    function renderQueue() {
      const root = document.getElementById("queueList");
      const leads = session.available_leads || [];
      root.innerHTML = leads.map(lead => {
        const active = session && session.lead_context && session.lead_context.Lead_ID === lead.lead_id ? "active" : "";
        return `
          <button class="queue-item ${active}" onclick="loadQueueLead('${escapeJs(lead.lead_id)}', '${escapeJs(lead.company)}', '${escapeJs(lead.project_type)}', '${escapeJs(lead.address)}', '${escapeJs(lead.contact_name)}')">
            <strong>${escapeHtml(lead.lead_id)}</strong>
            <span>${escapeHtml(lead.company)} | ${escapeHtml(lead.project_type)}</span>
            <div class="badge-row">
              <span class="badge">${escapeHtml(lead.address)}</span>
            </div>
          </button>`;
      }).join("");
    }

    function loadQueueLead(leadId, company, projectType, address, contactName) {
      document.getElementById("newLeadId").value = leadId;
      document.getElementById("newLeadNotes").value = `Load ${projectType.toLowerCase()} request for ${company}.`;
      createOrSwitchSession({
        Company: company,
        Contact_Name: contactName,
        Project_Type: projectType,
        Address_Input: address
      });
    }

    function renderSourceContext() {
      const root = document.getElementById("sourceContext");
      const items = session.source_context || [];
      if (!items.length) {
        root.innerHTML = `<div class="empty-state">No retrieved sources yet. Run the quote to load recipe, compliance, and quote provenance.</div>`;
        return;
      }
      root.innerHTML = items.map(item => `
        <div class="source-row">
          <div>
            <strong>${escapeHtml(item.label)}</strong>
            <div class="muted">${escapeHtml(item.source)}</div>
          </div>
          <div class="source-tag ${statusClass(item.status)}">${escapeHtml(item.status)} | ${escapeHtml(shortTime(item.timestamp))}</div>
        </div>
      `).join("");
    }

    function renderTimeline() {
      const root = document.getElementById("timeline");
      const items = [];
      (session.messages || []).forEach(msg => items.push({ type: "message", payload: msg }));
      if (session.quote_draft) items.push({ type: "quote", payload: session.quote_draft });
      if (session.compliance_rules && session.compliance_rules.length) items.push({ type: "codes", payload: session.compliance_rules });
      if (session.comm_draft) items.push({ type: "email", payload: session.comm_draft });
      if (session.current_view && session.current_view.kind === "sent") items.push({ type: "sent", payload: session.current_view.payload });

      root.innerHTML = items.map(item => {
        if (item.type === "message") return renderMessage(item.payload);
        if (item.type === "quote") return renderQuoteCard(item.payload);
        if (item.type === "codes") return renderComplianceCard(item.payload);
        if (item.type === "email") return renderEmailCard(item.payload);
        if (item.type === "sent") return renderNoticeCard(item.payload, "Customer email sent");
        return "";
      }).join("");
      root.scrollTop = root.scrollHeight;
    }

    function renderMessage(message) {
      const roleClass = message.role === "rep" ? "rep" : "";
      return `
        <div class="message ${roleClass}">
          <div class="message-meta">${escapeHtml(message.role || "sage")} | ${escapeHtml(shortTime(message.timestamp))}</div>
          <div class="message-text">${escapeHtml(message.text || "")}</div>
        </div>
      `;
    }

    function renderQuoteCard(quote) {
      const lead = session.lead_context || {};
      const rules = session.compliance_rules || [];
      const codeReview = session.code_review || [];
      const recipe = session.project_recipe;
      return `
        <div class="message">
          <div class="message-meta">sage | ${escapeHtml(shortTime(nowIso()))}</div>
          <div class="message-text">Mustang Sage assembled a draft quote from lead context, recipe history, and municipal code review.</div>
          <div class="quote-card">
            <div class="card-hero">
              <h3>${escapeHtml(quote.Project_Name || "Quote Draft")}</h3>
              <p>${escapeHtml(lead.Company || "")} | ${escapeHtml(lead.Project_Type || "")} | ${escapeHtml(quote.Quote_ID || "")}</p>
            </div>
            <div class="card-grid">
              <div class="card-section">
                <div class="section-title">Quote Summary</div>
                <div class="fact-grid">
                  ${factRow("Customer", lead.Company)}
                  ${factRow("Contact", lead.Contact_Name)}
                  ${factRow("Address", lead.Address_Input)}
                  ${factRow("Travel SKU", quote.Travel_SKU)}
                  ${factRow("Travel Fee", money(quote.Travel_Fee_Amount))}
                  ${factRow("Permit Fees", money(quote.Permit_Fees))}
                  ${factRow("Gross Margin", percent(quote.Gross_Margin_Pct))}
                  ${factRow("Status", quote.Status)}
                </div>

                <div class="section-title" style="margin-top:8px;">Line Items</div>
                <div class="line-items">
                  ${(quote.Line_Items || []).map(item => `
                    <div class="line-row">
                      <div><strong>${escapeHtml(item.Description || item.SKU || "Item")}</strong><div class="muted">${escapeHtml(item.SKU || "")}</div></div>
                      <div>${escapeHtml(String(item.Qty || 1))}</div>
                      <div>${escapeHtml(item.Unit_Price !== undefined ? money(item.Unit_Price) : "editable")}</div>
                      <div>${escapeHtml(item.Price !== undefined ? money(item.Price) : "custom")}</div>
                    </div>
                  `).join("") || '<div class="empty-state">No line items yet.</div>'}
                </div>
              </div>
              <div class="card-section">
                <div class="section-title">Municipal Codes</div>
                <div class="compliance-list">
                  ${rules.map((rule, index) => `
                    <div class="compliance-row">
                      <div>
                        <strong>${escapeHtml(rule.Jurisdiction_Name)} | ${escapeHtml(rule.Code_Citation)}</strong>
                        <div class="muted">Height ${escapeHtml(String(rule.Height_Limit_Ft || ""))} ft | Setback ${escapeHtml(String(rule.Setback_Ft || ""))} ft | Max ${escapeHtml(String(rule.Max_Sq_Ft || ""))} sq ft</div>
                        <div class="muted">${escapeHtml(rule.Illumination_Notes || "")}</div>
                      </div>
                      <div class="status-pill ${codeReviewClass(codeReview[index] ? codeReview[index].status : "acknowledged")}">${escapeHtml((codeReview[index] && codeReview[index].status) || "acknowledged")}</div>
                    </div>
                  `).join("") || '<div class="empty-state">No municipal rules loaded yet.</div>'}
                </div>

                <div class="section-title" style="margin-top:8px;">Retrieved Context</div>
                <div class="source-list">
                  ${recipe ? sourceRow("Recipe", recipe.Recipe_ID, "Retrieved") : ""}
                  ${sourceRow("Address Geo-Lock", lead.Address_Geo_Lock ? `${lead.Address_Geo_Lock.lat}, ${lead.Address_Geo_Lock.lng}` : "pending", lead.Address_Geo_Lock ? "Inferred" : "Pending")}
                  ${sourceRow("Quote Assembly", quote.Quote_ID, "Inferred")}
                </div>
              </div>
            </div>
            <div class="card-actions" style="padding:16px 20px; border-top:1px solid var(--teams-border);">
              <button class="action-button primary" onclick="approveQuote()">Approve Quote</button>
              <button class="action-button" onclick="showTab('quote')">Edit Quote</button>
              <button class="action-button" onclick="showTab('codes')">Review Codes</button>
              <button class="action-button" onclick="regenerateQuote()">Manual Regenerate</button>
            </div>
          </div>
        </div>
      `;
    }

    function renderComplianceCard(rules) {
      return `
        <div class="message">
          <div class="message-meta">sage | ${escapeHtml(shortTime(nowIso()))}</div>
          <div class="message-text">Municipal code constraints are visible beside the quote and editable for acknowledgement or review state.</div>
          <div class="notice-card">
            <div class="card-hero">
              <h3>Code Review Snapshot</h3>
              <p>${escapeHtml(session.lead_context.Address_Input || "")}</p>
            </div>
            <div class="card-section">
              <div class="compliance-list">
                ${rules.map((rule, index) => `
                  <div class="compliance-row">
                    <div>
                      <strong>${escapeHtml(rule.Jurisdiction_Name)} | ${escapeHtml(rule.Code_Citation)}</strong>
                      <div class="muted">Permit ${money(rule.Permit_Fee)} | Height ${escapeHtml(String(rule.Height_Limit_Ft || ""))} ft | Setback ${escapeHtml(String(rule.Setback_Ft || ""))} ft</div>
                    </div>
                    <div class="status-pill ${codeReviewClass((session.code_review[index] || {}).status || "acknowledged")}">${escapeHtml((session.code_review[index] || {}).status || "acknowledged")}</div>
                  </div>
                `).join("")}
              </div>
            </div>
          </div>
        </div>
      `;
    }

    function renderEmailCard(email) {
      return `
        <div class="message">
          <div class="message-meta">sage | ${escapeHtml(shortTime(nowIso()))}</div>
          <div class="message-text">Customer follow-up draft is ready for preview, edit, and confirmation.</div>
          <div class="email-card">
            <div class="card-hero">
              <h3>${escapeHtml(email.Subject || "Customer Email")}</h3>
              <p>${escapeHtml(session.lead_context.Company || "")} | ${escapeHtml(email.Status || "draft")}</p>
            </div>
            <div class="card-section">
              <div class="fact-grid">
                ${factRow("Draft ID", email.Draft_ID)}
                ${factRow("Grounded To", email.Grounded_To)}
                ${factRow("Recipient", email.Recipient_Email || "Simulated")}
                ${factRow("Status", email.Status)}
              </div>
              <div class="empty-state">${escapeHtml(email.Body || "")}</div>
            </div>
            <div class="card-actions" style="padding:16px 20px; border-top:1px solid var(--teams-border);">
              <button class="action-button" onclick="showTab('email')">Edit Email</button>
              <button class="action-button primary" onclick="confirmSend()">Confirm Send</button>
            </div>
          </div>
        </div>
      `;
    }

    function renderNoticeCard(payload, title) {
      return `
        <div class="message">
          <div class="message-meta">sage | ${escapeHtml(shortTime(nowIso()))}</div>
          <div class="notice-card">
            <div class="card-hero">
              <h3>${escapeHtml(title)}</h3>
              <p>${escapeHtml(payload.subtitle || "")}</p>
            </div>
            <div class="card-section">
              <div class="empty-state">${escapeHtml(payload.body || "")}</div>
            </div>
          </div>
        </div>
      `;
    }

    function hydrateLeadFields() {
      const lead = session.lead_context || {};
      setValue("leadId", lead.Lead_ID || "");
      setValue("pipelineStage", lead.Pipeline_Stage || "");
      setValue("company", lead.Company || "");
      setValue("contactName", lead.Contact_Name || "");
      setValue("projectType", lead.Project_Type || "Monument Sign");
      setValue("lastActivity", lead.Last_Activity_Date || "");
      setValue("addressInput", lead.Address_Input || "");
      setValue("openNotes", lead.Open_Notes || "");
    }

    function hydrateQuoteFields() {
      const quote = session.quote_draft || {};
      setValue("quoteId", quote.Quote_ID || "");
      setValue("projectName", quote.Project_Name || "");
      setValue("travelSku", quote.Travel_SKU || session.travel_sku || "");
      setValue("travelFee", quote.Travel_Fee_Amount ?? "");
      setValue("permitFees", quote.Permit_Fees ?? "");
      setValue("grossMargin", quote.Gross_Margin_Pct ?? "");
      renderLineItemEditor(quote.Line_Items || []);
    }

    function hydrateCodeReview() {
      const root = document.getElementById("codeReviewEditor");
      const review = session.code_review || [];
      const rules = session.compliance_rules || [];
      if (!rules.length) {
        root.innerHTML = `<div class="empty-state">Run the quote workflow to load jurisdiction rules.</div>`;
        return;
      }
      root.innerHTML = rules.map((rule, index) => {
        const item = review[index] || {};
        return `
          <div class="quick-create" style="margin-bottom:12px;">
            <strong>${escapeHtml(rule.Jurisdiction_Name)} | ${escapeHtml(rule.Code_Citation)}</strong>
            <div class="muted" style="margin-top:6px;">Height ${escapeHtml(String(rule.Height_Limit_Ft || ""))} ft | Setback ${escapeHtml(String(rule.Setback_Ft || ""))} ft | Max ${escapeHtml(String(rule.Max_Sq_Ft || ""))} sq ft</div>
            <div class="field-grid" style="margin-top:12px;">
              <label class="field">
                Review Status
                <select data-code-status="${index}">
                  ${option(item.status || "acknowledged", "acknowledged")}
                  ${option(item.status || "acknowledged", "needs_review")}
                </select>
              </label>
              <label class="field full">
                Internal Override Notes
                <textarea data-code-note="${index}" placeholder="Explain why this stays compliant or requires review.">${escapeHtml(item.note || "")}</textarea>
              </label>
            </div>
          </div>
        `;
      }).join("");
    }

    function hydrateEmailDraft() {
      const email = session.comm_draft || {};
      setValue("emailSubject", email.Subject || "");
      setValue("emailBody", email.Body || "");
    }

    function renderFieldSources() {
      const root = document.getElementById("detailFieldSources");
      const fields = session.field_sources || {};
      const keys = ["Company", "Contact_Name", "Project_Type", "Last_Activity_Date", "Address_Input", "Open_Notes", "Quote", "Compliance", "Email"];
      root.innerHTML = keys.filter(key => fields[key]).map(key => {
        const item = fields[key];
        return `<span class="source-tag ${statusClass(item.status)}">${escapeHtml(key)} | ${escapeHtml(item.status)} | ${escapeHtml(shortTime(item.timestamp))}</span>`;
      }).join("");
    }

    function renderLineItemEditor(items) {
      const root = document.getElementById("lineItemEditor");
      root.innerHTML = (items || []).map((item, index) => `
        <div class="line-edit-row" data-line-index="${index}">
          <div class="line-cell"><input data-line-sku="${index}" value="${escapeAttr(item.SKU || "")}" placeholder="SKU" /></div>
          <div class="line-cell"><input data-line-qty="${index}" type="number" step="1" value="${escapeAttr(item.Qty ?? 1)}" placeholder="Qty" /></div>
          <div class="line-cell"><input data-line-price="${index}" type="number" step="0.01" value="${escapeAttr(item.Price ?? item.Unit_Price ?? "")}" placeholder="Price" /></div>
          <div class="line-cell"><textarea data-line-desc="${index}" placeholder="Description">${escapeHtml(item.Description || "")}</textarea></div>
          <div><button class="mini-button" onclick="removeLineItem(${index})">Remove</button></div>
        </div>
      `).join("") || `<div class="empty-state">No line items yet. Add custom rows below.</div>`;
    }

    function collectLineItems() {
      const rows = document.querySelectorAll("[data-line-index]");
      return Array.from(rows).map(row => {
        const index = row.getAttribute("data-line-index");
        return {
          SKU: document.querySelector(`[data-line-sku="${index}"]`).value.trim(),
          Qty: Number(document.querySelector(`[data-line-qty="${index}"]`).value || 1),
          Price: Number(document.querySelector(`[data-line-price="${index}"]`).value || 0),
          Description: document.querySelector(`[data-line-desc="${index}"]`).value.trim() || "Custom item"
        };
      });
    }

    function addLineItem() {
      const items = collectLineItems();
      items.push({ SKU: "CUSTOM", Qty: 1, Price: 0, Description: "Custom item" });
      renderLineItemEditor(items);
    }

    function removeLineItem(index) {
      const items = collectLineItems().filter((_, idx) => idx !== index);
      renderLineItemEditor(items);
    }

    function collectCodeReview() {
      return (session.compliance_rules || []).map((rule, index) => ({
        Code_Citation: rule.Code_Citation,
        Jurisdiction: rule.Jurisdiction,
        Jurisdiction_Name: rule.Jurisdiction_Name,
        status: document.querySelector(`[data-code-status="${index}"]`).value,
        note: document.querySelector(`[data-code-note="${index}"]`).value.trim()
      }));
    }

    function showTab(tabName) {
      currentTab = tabName;
      document.querySelectorAll(".tab").forEach(tab => tab.classList.toggle("active", tab.dataset.tab === tabName));
      document.querySelectorAll(".detail-section").forEach(section => section.classList.remove("active"));
      document.getElementById(`tab-${tabName}`).classList.add("active");
      if (debugVisible) document.getElementById("debugPanel").classList.add("active");
    }

    function toggleDebug() {
      debugVisible = !debugVisible;
      document.getElementById("debugPanel").classList.toggle("active", debugVisible);
    }

    function factRow(label, value) {
      return `<div class="fact-row"><div class="fact-label">${escapeHtml(label)}</div><div>${escapeHtml(value === undefined || value === null ? "" : String(value))}</div></div>`;
    }

    function sourceRow(label, source, status) {
      return `
        <div class="source-row">
          <div><strong>${escapeHtml(label)}</strong><div class="muted">${escapeHtml(source || "")}</div></div>
          <div class="source-tag ${statusClass(status)}">${escapeHtml(status)}</div>
        </div>
      `;
    }

    function codeReviewClass(status) {
      if (status === "needs_review") return "review";
      if (status === "acknowledged") return "ok";
      return "draft";
    }

    function statusClass(status) {
      const value = (status || "").toLowerCase();
      if (value.includes("retrieved")) return "retrieved";
      if (value.includes("inferred")) return "inferred";
      if (value.includes("user")) return "user";
      return "";
    }

    function option(current, valueText) {
      const selected = current === valueText ? "selected" : "";
      return `<option value="${valueText}" ${selected}>${valueText}</option>`;
    }

    function money(value) {
      const num = Number(value || 0);
      return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(num);
    }

    function percent(value) {
      return `${(Number(value || 0) * 100).toFixed(1)}%`;
    }

    function value(id) {
      return document.getElementById(id).value.trim();
    }

    function numberValue(id) {
      const raw = document.getElementById(id).value;
      return raw === "" ? null : Number(raw);
    }

    function setValue(id, value) {
      const el = document.getElementById(id);
      if (el) el.value = value ?? "";
    }

    function setStatus(text) {
      document.getElementById("statusBadge").textContent = text;
    }

    function nowIso() {
      return new Date().toISOString();
    }

    function shortTime(value) {
      if (!value) return "";
      return new Date(value).toLocaleString();
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function escapeAttr(value) {
      return escapeHtml(value).replaceAll("\\n", " ");
    }

    function escapeJs(value) {
      return String(value ?? "").replaceAll("\\\\", "\\\\\\\\").replaceAll("'", "\\\\'");
    }

    showTab("details");
    createOrSwitchSession();
  </script>
</body>
</html>"""
