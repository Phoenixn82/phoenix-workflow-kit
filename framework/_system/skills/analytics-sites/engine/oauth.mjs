import { randomBytes } from "node:crypto";
import { postForm } from "./http.mjs";

export const GOOGLE_READONLY_SCOPES = [
  "https://www.googleapis.com/auth/analytics.readonly",
  "https://www.googleapis.com/auth/webmasters.readonly"
];

export function buildGoogleConsentUrl(source, options = {}) {
  const env = options.env || process.env;
  const redirectUri = env.GOOGLE_OAUTH_REDIRECT_URI || options.redirectUri || `${options.origin || "http://localhost:8787"}/oauth/callback`;
  const state = options.state || createState(source);
  const scopes = Array.isArray(options.scopes) && options.scopes.length
    ? options.scopes
    : GOOGLE_READONLY_SCOPES;
  const url = new URL("https://accounts.google.com/o/oauth2/v2/auth");

  url.searchParams.set("client_id", env.GOOGLE_OAUTH_CLIENT_ID || "");
  url.searchParams.set("redirect_uri", redirectUri);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", scopes.join(" "));
  url.searchParams.set("access_type", "offline");
  url.searchParams.set("prompt", "consent");
  url.searchParams.set("state", state);

  return url.toString();
}

export function createState(source) {
  const payload = JSON.stringify({
    source,
    nonce: randomBytes(12).toString("hex")
  });
  return Buffer.from(payload).toString("base64url");
}

export function parseState(value) {
  try {
    return JSON.parse(Buffer.from(String(value || ""), "base64url").toString("utf8"));
  } catch {
    return {};
  }
}

const DEFAULT_STATE_TTL_MS = 10 * 60 * 1000;

// CSRF protection for the OAuth round-trip. `issue` mints a one-time nonce,
// remembers it server-side with a TTL, and returns the encoded state. `consume`
// only resolves a source for a state whose nonce is still pending, unexpired,
// and matches the source it was issued for — otherwise the callback is rejected.
export function createStateStore({ ttlMs = DEFAULT_STATE_TTL_MS, now = () => Date.now() } = {}) {
  const pending = new Map();

  function prune(currentTime) {
    for (const [nonce, entry] of pending) {
      if (entry.expiresAt <= currentTime) pending.delete(nonce);
    }
  }

  return {
    issue(source) {
      const currentTime = now();
      prune(currentTime);
      const nonce = randomBytes(12).toString("hex");
      pending.set(nonce, { source, expiresAt: currentTime + ttlMs });
      return Buffer.from(JSON.stringify({ source, nonce })).toString("base64url");
    },
    consume(stateValue) {
      const parsed = parseState(stateValue);
      const nonce = parsed?.nonce;
      if (!nonce) return null;
      const entry = pending.get(nonce);
      if (!entry) return null;
      if (entry.expiresAt <= now()) {
        pending.delete(nonce);
        return null;
      }
      if (entry.source !== parsed.source) return null;
      pending.delete(nonce);
      return { source: entry.source };
    },
    get size() {
      return pending.size;
    }
  };
}

export async function exchangeCodeForTokens({ code, env = process.env, fetch = globalThis.fetch, redirectUri }) {
  return postForm("https://oauth2.googleapis.com/token", {
    client_id: env.GOOGLE_OAUTH_CLIENT_ID || "",
    client_secret: env.GOOGLE_OAUTH_CLIENT_SECRET || "",
    code,
    grant_type: "authorization_code",
    redirect_uri: redirectUri || env.GOOGLE_OAUTH_REDIRECT_URI || "http://localhost:8787/oauth/callback"
  }, fetch);
}

export async function refreshAccessToken({ refreshToken, env = process.env, fetch = globalThis.fetch }) {
  const data = await postForm("https://oauth2.googleapis.com/token", {
    client_id: env.GOOGLE_OAUTH_CLIENT_ID || "",
    client_secret: env.GOOGLE_OAUTH_CLIENT_SECRET || "",
    refresh_token: refreshToken,
    grant_type: "refresh_token"
  }, fetch);
  return data.access_token;
}
