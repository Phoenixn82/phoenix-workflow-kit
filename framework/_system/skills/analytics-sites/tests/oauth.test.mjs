import assert from "node:assert/strict";
import test from "node:test";
import { buildGoogleConsentUrl, createStateStore } from "../engine/oauth.mjs";

test("Google OAuth consent URL uses read-only scopes, offline access, consent prompt, state, and configured redirect URI", () => {
  const url = new URL(buildGoogleConsentUrl("ga4", {
    env: {
      GOOGLE_OAUTH_CLIENT_ID: "client-id",
      GOOGLE_OAUTH_REDIRECT_URI: "http://localhost:8787/oauth/callback"
    },
    state: "state-value"
  }));

  assert.equal(url.origin + url.pathname, "https://accounts.google.com/o/oauth2/v2/auth");
  assert.equal(url.searchParams.get("client_id"), "client-id");
  assert.equal(url.searchParams.get("redirect_uri"), "http://localhost:8787/oauth/callback");
  assert.equal(url.searchParams.get("access_type"), "offline");
  assert.equal(url.searchParams.get("prompt"), "consent");
  assert.equal(url.searchParams.get("state"), "state-value");
  assert.match(url.searchParams.get("scope"), /analytics\.readonly/);
  assert.match(url.searchParams.get("scope"), /webmasters\.readonly/);
});

test("Google OAuth consent URL honors a connector's declared per-source scopes", () => {
  const url = new URL(buildGoogleConsentUrl("gsc", {
    env: { GOOGLE_OAUTH_CLIENT_ID: "client-id" },
    state: "state-value",
    scopes: ["https://www.googleapis.com/auth/webmasters.readonly"]
  }));

  assert.equal(url.searchParams.get("scope"), "https://www.googleapis.com/auth/webmasters.readonly");
});

test("OAuth state store issues a one-time nonce and rejects forgeries, replays, and expiry", () => {
  let clock = 1000;
  const store = createStateStore({ ttlMs: 100, now: () => clock });

  // Unparseable / missing state is never accepted (no defaulting to a source).
  assert.equal(store.consume(""), null);
  assert.equal(store.consume("not-a-real-state"), null);
  assert.equal(store.consume(null), null);

  // A state whose nonce was never issued is rejected.
  const unknown = Buffer.from(JSON.stringify({ source: "ga4", nonce: "deadbeef" }), "utf8").toString("base64url");
  assert.equal(store.consume(unknown), null);

  // A genuinely issued state resolves to its source exactly once (replay rejected).
  const issued = store.issue("gsc");
  assert.deepEqual(store.consume(issued), { source: "gsc" });
  assert.equal(store.consume(issued), null);

  // A forged source on a real nonce is rejected without burning the nonce.
  const real = store.issue("ga4");
  const decoded = JSON.parse(Buffer.from(real, "base64url").toString("utf8"));
  const forged = Buffer.from(JSON.stringify({ source: "gsc", nonce: decoded.nonce }), "utf8").toString("base64url");
  assert.equal(store.consume(forged), null);
  assert.deepEqual(store.consume(real), { source: "ga4" });

  // An expired nonce is rejected.
  const stale = store.issue("gsc");
  clock += 101;
  assert.equal(store.consume(stale), null);
});
