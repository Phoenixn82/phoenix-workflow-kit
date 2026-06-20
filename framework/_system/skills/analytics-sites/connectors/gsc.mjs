import { assertFreeEndpoint } from "../engine/free-only-guard.mjs";
import { postJson } from "../engine/http.mjs";

const ENDPOINT = {
  id: "gsc",
  currentTier: "included_account_api",
  cost: "free_google_account_quota"
};

export function createGscConnector() {
  return {
    id: "gsc",
    label: "Google Search Console",
    auth: {
      type: "google_oauth",
      scopes: ["https://www.googleapis.com/auth/webmasters.readonly"]
    },
    connectUrl: () => "/connect/gsc",
    async isConnected(ctx) {
      return Boolean(await ctx.tokenStore?.getRefreshToken("gsc"));
    },
    async fetch(ctx) {
      assertFreeEndpoint(ENDPOINT);
      const siteUrl = ctx.config?.sources?.gsc?.siteUrl || "";
      if (!siteUrl) throw new Error("Search Console site is not selected.");

      const data = await postJson(
        `https://searchconsole.googleapis.com/webmasters/v3/sites/${encodeURIComponent(siteUrl)}/searchAnalytics/query`,
        ctx.accessToken,
        {
          startDate: ctx.startDate || dateOffset(-29),
          endDate: ctx.endDate || dateOffset(0),
          dimensions: ["date"],
          rowLimit: 1000
        },
        ctx.fetch
      );

      const rows = (data.rows || []).map((row) => ({
        date: row.keys?.[0] || "",
        clicks: number(row.clicks),
        impressions: number(row.impressions),
        ctr: number(row.ctr),
        position: number(row.position)
      }));

      return [
        metric("clicks", "Organic clicks", rows, "clicks"),
        metric("impressions", "Search impressions", rows, "impressions")
      ];
    },
    async healthcheck(ctx) {
      return (await this.isConnected(ctx))
        ? { status: "connected", detail: "Search Console token is stored." }
        : { status: "connect", detail: "Connect Search Console." };
    }
  };
}

function metric(key, label, rows, rowKey) {
  const series = rows.map((row) => ({
    date: row.date,
    value: number(row[rowKey])
  }));
  return {
    source: "gsc",
    key,
    label,
    value: series.reduce((total, point) => total + point.value, 0),
    unit: "",
    series
  };
}

function dateOffset(days) {
  const date = new Date(Date.now() + days * 24 * 60 * 60 * 1000);
  return date.toISOString().slice(0, 10);
}

function number(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}
