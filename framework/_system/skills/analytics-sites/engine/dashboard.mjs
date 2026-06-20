export const SOURCE_LABELS = {
  ga4: "Google Analytics 4",
  gsc: "Google Search Console",
  gbp: "Google Business Profile",
  smsleads: "SMS Leads",
  vercel: "Vercel",
  pagespeed: "PageSpeed / Lighthouse"
};

export function buildBlankSnapshot(config, sourceStates = {}) {
  const cards = config.cards || Object.keys(SOURCE_LABELS);
  const sources = cards.map((id) => ({
    id,
    label: SOURCE_LABELS[id] || id,
    status: sourceStates[id]?.status || "connect",
    detail: sourceStates[id]?.detail || `Connect ${SOURCE_LABELS[id] || id}.`,
    lastSyncedAt: null,
    metrics: []
  }));

  return {
    generatedAt: new Date().toISOString(),
    business: {
      name: config.company?.name || "Analytics Site",
      tagline: config.company?.tagline || "",
      domains: config.company?.domains || []
    },
    summary: {
      health: "Connect",
      connectedSources: sources.filter((source) => source.status === "connected").length,
      totalSources: sources.length,
      nextAction: "Connect Google Analytics or Search Console."
    },
    sources,
    scorecards: sources.map((source) => ({
      id: source.id,
      label: source.label,
      value: null,
      unit: "",
      source: source.label,
      status: source.status,
      detail: source.detail
    }))
  };
}

export function renderDashboard(snapshot) {
  const payload = JSON.stringify(redactSnapshot(snapshot)).replace(/</g, "\\u003c");
  const cards = (snapshot.scorecards || []).map((card) => {
    const source = findSource(snapshot, card);
    return `
      <article class="card source-card" data-source="${escapeHtml(card.source)}" data-status="${escapeHtml(source.status)}">
        <div>
          <div class="label">${escapeHtml(card.label)}</div>
          <div class="value">${escapeHtml(cardValue(card, source))}</div>
          <div class="detail">${escapeHtml(source.detail || card.detail || "")}</div>
        </div>
        ${sourceAction(source)}
      </article>`;
  }).join("");

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(snapshot.business?.name)} Analytics</title>
  <style>
    :root { color-scheme: light; --ink: #17211d; --muted: #62706a; --line: #d8dfdc; --paper: #f6f7f3; --panel: #ffffff; --green: #15734b; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--paper); color: var(--ink); font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; letter-spacing: 0; }
    .shell { min-height: 100vh; display: grid; grid-template-columns: 260px 1fr; }
    aside { background: #25302b; color: white; padding: 24px; display: grid; align-content: space-between; gap: 24px; }
    main { padding: 28px; display: grid; gap: 22px; }
    h1, h2, p { margin: 0; }
    h1 { font-size: 38px; line-height: 1.05; letter-spacing: 0; max-width: 900px; }
    .subtle { color: var(--muted); line-height: 1.45; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(180px, 1fr)); gap: 14px; }
    .card, .panel { background: var(--panel); border: 1px solid var(--line); border-radius: 8px; }
    .card { min-height: 148px; padding: 16px; display: grid; align-content: space-between; gap: 16px; }
    .label { color: var(--muted); font-size: 13px; line-height: 1.35; }
    .value { font-size: 30px; font-weight: 850; line-height: 1; letter-spacing: 0; }
    .detail { color: var(--muted); font-size: 12px; line-height: 1.35; min-height: 16px; }
    .connect { color: var(--green); font-weight: 800; text-decoration: none; }
    .status-text { color: var(--muted); font-weight: 800; }
    .panel { padding: 18px; }
    .source-list { display: grid; gap: 10px; }
    .source-row { display: grid; grid-template-columns: minmax(160px, 1fr) auto; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--line); }
    .source-row:last-child { border-bottom: 0; }
    .source-row small { display: block; color: var(--muted); margin-top: 3px; line-height: 1.35; }
    .pill { border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; font-size: 12px; font-weight: 800; }
    @media (max-width: 920px) { .shell { grid-template-columns: 1fr; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="shell">
    <aside>
      <div>
        <h2>${escapeHtml(snapshot.business?.name)}</h2>
        <p>${escapeHtml(snapshot.business?.tagline)}</p>
      </div>
      <p>${snapshot.summary.connectedSources} of ${snapshot.summary.totalSources} sources connected</p>
    </aside>
    <main>
      <section>
        <p class="subtle">Sites analytics</p>
        <h1>${escapeHtml(snapshot.business?.name)} analytics dashboard</h1>
        <p class="subtle">${escapeHtml(snapshot.summary.nextAction)}</p>
      </section>
      <section class="grid" aria-label="Source cards">
        ${cards}
      </section>
      <section class="panel">
        <h2>Source Health</h2>
        <div class="source-list">
          ${(snapshot.sources || []).map((source) => `
            <div class="source-row">
              <span>${escapeHtml(source.label)}<small>${escapeHtml(source.detail || "")}</small></span>
              <span class="pill">${escapeHtml(statusLabel(source.status))}</span>
            </div>`).join("")}
        </div>
      </section>
    </main>
  </div>
  <script id="snapshot-data" type="application/json">${payload}</script>
</body>
</html>`;
}

function findSource(snapshot, card) {
  return (snapshot.sources || []).find((source) => source.id === card.id || source.label === card.source) || {
    id: card.id || "",
    label: card.source || card.label || "",
    status: card.status || "connect",
    detail: card.detail || ""
  };
}

function cardValue(card, source) {
  if (source.status === "connected" && card.value !== null && card.value !== undefined) {
    return formatMetricValue(card.value, card.unit);
  }
  return statusLabel(source.status);
}

function sourceAction(source) {
  if (source.status === "connect") {
    return `<a class="connect" href="/connect/${escapeHtml(source.id)}">Connect</a>`;
  }
  return `<span class="status-text">${escapeHtml(statusLabel(source.status))}</span>`;
}

function statusLabel(status) {
  const labels = {
    connected: "Connected",
    connect: "Connect",
    "needs setup": "Needs setup",
    error: "Error",
    blocked: "Blocked"
  };
  return labels[status] || status || "Connect";
}

function formatMetricValue(value, unit = "") {
  const numeric = Number(value);
  const formatted = Number.isFinite(numeric) ? numeric.toLocaleString("en-US") : String(value);
  return unit ? `${formatted} ${unit}` : formatted;
}

function redactSnapshot(snapshot) {
  return JSON.parse(JSON.stringify(snapshot));
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  }[char]));
}
