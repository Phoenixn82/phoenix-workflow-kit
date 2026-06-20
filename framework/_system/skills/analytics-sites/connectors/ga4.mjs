import { assertFreeEndpoint } from "../engine/free-only-guard.mjs";
import { postJson } from "../engine/http.mjs";

const ENDPOINT = {
  id: "ga4",
  currentTier: "included_account_api",
  cost: "free_google_account_quota"
};

export function createGa4Connector() {
  return {
    id: "ga4",
    label: "Google Analytics 4",
    auth: {
      type: "google_oauth",
      scopes: ["https://www.googleapis.com/auth/analytics.readonly"]
    },
    connectUrl: () => "/connect/ga4",
    async isConnected(ctx) {
      return Boolean(await ctx.tokenStore?.getRefreshToken("ga4"));
    },
    async fetch(ctx) {
      assertFreeEndpoint(ENDPOINT);
      const propertyId = String(ctx.config?.sources?.ga4?.propertyId || "").replace(/^properties\//, "");
      if (!propertyId) throw new Error("GA4 property is not selected.");

      const data = await postJson(
        `https://analyticsdata.googleapis.com/v1beta/properties/${encodeURIComponent(propertyId)}:runReport`,
        ctx.accessToken,
        {
          dateRanges: [{ startDate: ctx.startDate || "30daysAgo", endDate: ctx.endDate || "today" }],
          dimensions: [{ name: "date" }],
          metrics: [{ name: "sessions" }, { name: "activeUsers" }],
          orderBys: [{ dimension: { dimensionName: "date" } }]
        },
        ctx.fetch
      );

      const rows = normalizedRows(data);
      return [
        metric("sessions", "Sessions", rows, 0),
        metric("activeUsers", "Active users", rows, 1)
      ];
    },
    async healthcheck(ctx) {
      return (await this.isConnected(ctx))
        ? { status: "connected", detail: "GA4 token is stored." }
        : { status: "connect", detail: "Connect Google Analytics 4." };
    }
  };
}

function normalizedRows(report) {
  return (report.rows || []).map((row) => ({
    date: row.dimensionValues?.[0]?.value || "",
    metrics: row.metricValues?.map((value) => number(value.value)) || []
  }));
}

function metric(key, label, rows, metricIndex) {
  const series = rows.map((row) => ({
    date: row.date,
    value: number(row.metrics[metricIndex])
  }));
  return {
    source: "ga4",
    key,
    label,
    value: series.reduce((total, point) => total + point.value, 0),
    unit: "",
    series
  };
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}
