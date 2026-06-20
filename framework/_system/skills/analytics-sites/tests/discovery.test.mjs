import assert from "node:assert/strict";
import test from "node:test";
import { discoverGa4Properties, discoverGoogleSources } from "../engine/discovery.mjs";

test("mock token discovery returns selectable GA4 properties and Search Console sites", async () => {
  const fetch = async (url) => {
    const href = String(url);
    if (href.includes("analyticsadmin.googleapis.com")) {
      return jsonResponse({
        accountSummaries: [
          {
            displayName: "Account",
            propertySummaries: [
              { property: "properties/123", displayName: "Example Co" }
            ]
          }
        ]
      });
    }
    if (href.includes("searchconsole.googleapis.com")) {
      return jsonResponse({
        siteEntry: [
          { siteUrl: "https://example.com/", permissionLevel: "siteOwner" }
        ]
      });
    }
    throw new Error(`Unexpected URL: ${href}`);
  };

  const result = await discoverGoogleSources({
    accessToken: "fake-token",
    fetch
  });

  assert.deepEqual(result.ga4, [
    { id: "123", label: "Example Co", rawId: "properties/123" }
  ]);
  assert.deepEqual(result.gsc, [
    { id: "https://example.com/", label: "https://example.com/", permissionLevel: "siteOwner" }
  ]);
});

test("GA4 discovery follows accountSummaries pagination and flattens property summaries", async () => {
  const calls = [];
  const fetch = async (url) => {
    const href = String(url);
    calls.push(href);
    const pageToken = new URL(href).searchParams.get("pageToken");
    if (!pageToken) {
      return jsonResponse({
        accountSummaries: [],
        nextPageToken: "next-page"
      });
    }
    return jsonResponse({
      accountSummaries: [
        {
          account: "accounts/456",
          displayName: "the user",
          propertySummaries: [
            { property: "properties/000000000", displayName: "Example Co Web" }
          ]
        }
      ]
    });
  };

  const result = await discoverGa4Properties({
    accessToken: "fake-token",
    fetch
  });

  assert.equal(calls.length, 2);
  assert.match(calls[0], /pageSize=200/);
  assert.match(calls[1], /pageToken=next-page/);
  assert.deepEqual(result, [
    { id: "000000000", label: "Example Co Web", rawId: "properties/000000000" }
  ]);
});

function jsonResponse(value) {
  return new Response(JSON.stringify(value), {
    headers: { "Content-Type": "application/json" }
  });
}
