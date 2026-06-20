import assert from "node:assert/strict";
import test from "node:test";
import { createGa4Connector } from "../connectors/ga4.mjs";
import { createGscConnector } from "../connectors/gsc.mjs";

test("GA4 connector normalizes runReport rows into KPI and series metrics", async () => {
  const connector = createGa4Connector();
  const calls = [];
  const fetch = async (url, options) => {
    calls.push({ url: String(url), body: JSON.parse(options.body) });
    return jsonResponse({
      rows: [
        {
          dimensionValues: [{ value: "2026-06-01" }],
          metricValues: [{ value: "10" }, { value: "6" }]
        },
        {
          dimensionValues: [{ value: "2026-06-02" }],
          metricValues: [{ value: "15" }, { value: "8" }]
        }
      ]
    });
  };

  const metrics = await connector.fetch({
    accessToken: "access-token",
    config: { sources: { ga4: { propertyId: "123456" } } },
    fetch
  });

  assert.match(calls[0].url, /analyticsdata\.googleapis\.com\/v1beta\/properties\/123456:runReport/);
  assert.deepEqual(metrics[0], {
    source: "ga4",
    key: "sessions",
    label: "Sessions",
    value: 25,
    unit: "",
    series: [
      { date: "2026-06-01", value: 10 },
      { date: "2026-06-02", value: 15 }
    ]
  });
  assert.deepEqual(metrics[1], {
    source: "ga4",
    key: "activeUsers",
    label: "Active users",
    value: 14,
    unit: "",
    series: [
      { date: "2026-06-01", value: 6 },
      { date: "2026-06-02", value: 8 }
    ]
  });
});

test("Search Console connector normalizes searchAnalytics rows into KPI and series metrics", async () => {
  const connector = createGscConnector();
  const fetch = async () => jsonResponse({
    rows: [
      { keys: ["2026-06-01"], clicks: 3, impressions: 100, ctr: 0.03, position: 8.2 },
      { keys: ["2026-06-02"], clicks: 5, impressions: 120, ctr: 0.0417, position: 7.6 }
    ]
  });

  const metrics = await connector.fetch({
    accessToken: "access-token",
    config: { sources: { gsc: { siteUrl: "https://example.com/" } } },
    fetch
  });

  assert.deepEqual(metrics[0], {
    source: "gsc",
    key: "clicks",
    label: "Organic clicks",
    value: 8,
    unit: "",
    series: [
      { date: "2026-06-01", value: 3 },
      { date: "2026-06-02", value: 5 }
    ]
  });
  assert.deepEqual(metrics[1], {
    source: "gsc",
    key: "impressions",
    label: "Search impressions",
    value: 220,
    unit: "",
    series: [
      { date: "2026-06-01", value: 100 },
      { date: "2026-06-02", value: 120 }
    ]
  });
});

function jsonResponse(value) {
  return new Response(JSON.stringify(value), {
    headers: { "Content-Type": "application/json" }
  });
}
