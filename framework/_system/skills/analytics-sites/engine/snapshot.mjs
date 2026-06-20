import { refreshAccessToken } from "./oauth.mjs";

export const SNAPSHOT_CACHE_TTL_MS = 5 * 60 * 1000;

const SOURCE_SELECTIONS = {
  ga4: { key: "propertyId", label: "GA4 property" },
  gsc: { key: "siteUrl", label: "Search Console site" }
};

export function createSnapshotCache(ttlMs = SNAPSHOT_CACHE_TTL_MS) {
  let cached = null;
  return {
    async get(factory) {
      const now = Date.now();
      if (cached && now - cached.createdAt < ttlMs) return cached.value;
      const value = await factory();
      cached = { createdAt: now, value };
      return value;
    },
    clear() {
      cached = null;
    }
  };
}

export async function buildLiveSnapshot({
  config,
  registry,
  tokenStore,
  env = process.env,
  fetch = globalThis.fetch,
  now = () => new Date()
}) {
  const generatedAt = now().toISOString();
  const cards = config.cards || registry.sourceRegistry?.map((source) => source.id) || [];
  const sources = await Promise.all(cards.map((id) => buildSourceState(id, {
    config,
    registry,
    tokenStore,
    env,
    fetch,
    generatedAt
  })));
  const connectedSources = sources.filter((source) => source.status === "connected").length;

  return {
    generatedAt,
    business: {
      name: config.company?.name || "Analytics Site",
      tagline: config.company?.tagline || "",
      domains: config.company?.domains || []
    },
    summary: {
      health: connectedSources > 0 ? "Live" : "Connect",
      connectedSources,
      totalSources: sources.length,
      nextAction: nextAction(sources)
    },
    sources,
    scorecards: sources.map(toScorecard)
  };
}

export async function fetchSourceMetrics(source, ctx) {
  const connector = ctx.registry.get(source);
  if (!connector) throw new Error("Unknown source.");

  const refreshToken = await ctx.tokenStore.getRefreshToken(source);
  if (!refreshToken) throw new Error(`Connect ${connector.label}.`);

  const accessToken = await refreshAccessToken({
    refreshToken,
    env: ctx.env || process.env,
    fetch: ctx.fetch || globalThis.fetch
  });
  return connector.fetch({
    ...ctx,
    accessToken,
    fetch: ctx.fetch || globalThis.fetch
  });
}

async function buildSourceState(id, ctx) {
  const connector = ctx.registry.get(id);
  const sourceConfig = ctx.config.sources?.[id] || {};
  const label = connector?.label || id;
  const base = {
    id,
    label,
    status: "connect",
    detail: `Connect ${label}.`,
    lastSyncedAt: null,
    metrics: []
  };

  if (!connector) {
    return { ...base, status: "needs setup", detail: "Source is not registered." };
  }
  if (sourceConfig.enabled === false) {
    return { ...base, status: "needs setup", detail: `${label} is not enabled in config.` };
  }

  const missingSelection = selectionGap(id, sourceConfig);
  if (missingSelection) {
    return { ...base, status: "needs setup", detail: `${missingSelection.label} is not selected.` };
  }

  if (connector.auth?.type === "google_oauth") {
    const refreshToken = await ctx.tokenStore.getRefreshToken(id);
    if (!refreshToken) return base;

    try {
      const metrics = await fetchSourceMetrics(id, ctx);
      return {
        ...base,
        status: "connected",
        detail: connectedDetail(label, metrics),
        lastSyncedAt: ctx.generatedAt,
        metrics
      };
    } catch (error) {
      return { ...base, status: "error", detail: safeError(error) };
    }
  }

  return { ...base, status: "needs setup", detail: `${label} does not have a live connector configured.` };
}

function selectionGap(id, sourceConfig) {
  const selection = SOURCE_SELECTIONS[id];
  return selection && !String(sourceConfig[selection.key] || "").trim() ? selection : null;
}

function connectedDetail(label, metrics) {
  const primary = metrics?.[0];
  if (!primary) return `${label} is connected.`;
  return `${primary.label}: ${formatNumber(primary.value)}${primary.unit ? ` ${primary.unit}` : ""}.`;
}

function toScorecard(source) {
  const primary = source.metrics?.[0];
  if (source.status === "connected" && primary) {
    return {
      id: source.id,
      label: primary.label,
      value: primary.value,
      unit: primary.unit || "",
      source: source.label,
      status: source.status,
      detail: source.detail
    };
  }
  return {
    id: source.id,
    label: source.label,
    value: null,
    unit: "",
    source: source.label,
    status: source.status,
    detail: source.detail
  };
}

function nextAction(sources) {
  const pending = sources.find((source) => source.status !== "connected");
  return pending ? pending.detail : "All selected sources are connected.";
}

function safeError(error) {
  const message = error?.message || String(error);
  return message.length > 180 ? `${message.slice(0, 177)}...` : message;
}

function formatNumber(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed.toLocaleString("en-US") : String(value);
}
