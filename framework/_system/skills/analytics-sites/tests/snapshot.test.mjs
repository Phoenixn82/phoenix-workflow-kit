import assert from "node:assert/strict";
import test from "node:test";
import { renderDashboard } from "../engine/dashboard.mjs";
import { createConnectorRegistry } from "../engine/registry.mjs";
import { buildLiveSnapshot } from "../engine/snapshot.mjs";

test("live snapshot fetches selected connected sources and renders real KPI values", async () => {
  const requestedUrls = [];
  const tokenStore = {
    async getRefreshToken(source) {
      return source === "gsc" || source === "ga4" ? `${source}-refresh-token` : "";
    }
  };
  const fetch = async (url) => {
    const href = String(url);
    requestedUrls.push(href);
    if (href === "https://oauth2.googleapis.com/token") {
      return jsonResponse({ access_token: "access-token" });
    }
    if (href.includes("searchconsole.googleapis.com")) {
      return jsonResponse({
        rows: [
          { keys: ["2026-06-01"], clicks: 4, impressions: 20, ctr: 0.2, position: 3 }
        ]
      });
    }
    throw new Error(`Unexpected URL: ${href}`);
  };

  const snapshot = await buildLiveSnapshot({
    config: {
      company: { name: "Example Co", tagline: "Hybrid repair", domains: ["example.com"] },
      sources: {
        ga4: { enabled: true, propertyId: "" },
        gsc: { enabled: true, siteUrl: "sc-domain:example.com" },
        gbp: { enabled: false }
      },
      cards: ["ga4", "gsc", "gbp"]
    },
    registry: createConnectorRegistry(),
    tokenStore,
    env: {
      GOOGLE_OAUTH_CLIENT_ID: "client-id",
      GOOGLE_OAUTH_CLIENT_SECRET: "client-secret"
    },
    fetch,
    now: () => new Date("2026-06-09T04:00:00.000Z")
  });

  const gsc = snapshot.sources.find((source) => source.id === "gsc");
  const ga4 = snapshot.sources.find((source) => source.id === "ga4");
  const gbp = snapshot.sources.find((source) => source.id === "gbp");
  const gscCard = snapshot.scorecards.find((card) => card.id === "gsc");
  const html = renderDashboard(snapshot);

  assert.equal(snapshot.summary.connectedSources, 1);
  assert.equal(gsc.status, "connected");
  assert.equal(gsc.metrics[0].value, 4);
  assert.equal(gsc.metrics[1].value, 20);
  assert.equal(gscCard.label, "Organic clicks");
  assert.equal(gscCard.value, 4);
  assert.equal(ga4.status, "needs setup");
  assert.match(ga4.detail, /property/i);
  assert.equal(gbp.status, "needs setup");
  assert.match(gbp.detail, /not enabled/i);
  assert.match(html, /Organic clicks/);
  assert.match(html, />4</);
  assert.match(html, /Connected/);
  assert.doesNotMatch(html, /data-source="Google Search Console"[\s\S]*<div class="value">Connect<\/div>/);
  assert.equal(requestedUrls.some((href) => href.includes("analyticsdata.googleapis.com")), false);
});

function jsonResponse(value) {
  return new Response(JSON.stringify(value), {
    headers: { "Content-Type": "application/json" }
  });
}
