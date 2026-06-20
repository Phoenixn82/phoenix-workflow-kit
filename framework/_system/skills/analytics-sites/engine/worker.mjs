import { mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { loadConfig, loadEnvFiles } from "./config.mjs";
import { renderDashboard } from "./dashboard.mjs";
import { discoverGoogleSources } from "./discovery.mjs";
import { buildGoogleConsentUrl, createStateStore, exchangeCodeForTokens, refreshAccessToken } from "./oauth.mjs";
import { createConnectorRegistry } from "./registry.mjs";
import { buildLiveSnapshot, createSnapshotCache, fetchSourceMetrics } from "./snapshot.mjs";
import { LocalFileTokenStore } from "./token-store.mjs";

export async function createWorker(options = {}) {
  const projectRoot = normalizeRoot(options.projectRoot || process.cwd());
  await loadEnvFiles(projectRoot, options.env || process.env);
  const configPath = options.configPath || join(projectRoot, "company.config.json");
  const config = await loadConfig(configPath);
  const registry = createConnectorRegistry();
  const tokenStore = options.tokenStore || new LocalFileTokenStore(join(projectRoot, ".analytics-sites", "tokens.json"));
  const stateStore = options.stateStore || createStateStore();
  const snapshotCache = createSnapshotCache(options.snapshotCacheTtlMs);
  await mkdir(join(projectRoot, ".analytics-sites"), { recursive: true });

  return {
    async fetch(request) {
      const url = new URL(request.url);

      if (url.pathname === "/health") {
        return json({ ok: true, service: "analytics-sites", company: config.company?.name || "" });
      }

      if (url.pathname === "/api/snapshot") {
        return json(await cachedSnapshot({ config, registry, tokenStore, snapshotCache }));
      }

      const connectMatch = url.pathname.match(/^\/connect\/([^/]+)$/);
      if (connectMatch) {
        const source = connectMatch[1];
        const connector = registry.get(source);
        if (!connector) return json({ status: "error", detail: "Unknown source." }, 404);
        if (connector.auth?.type !== "google_oauth") {
          return json({ status: "error", detail: `${connector.label} does not use Google OAuth.` }, 400);
        }
        return redirect(buildGoogleConsentUrl(source, {
          env: process.env,
          origin: url.origin,
          scopes: connector.auth?.scopes,
          state: stateStore.issue(source)
        }));
      }

      if (url.pathname === "/oauth/callback") {
        return handleCallback(url, tokenStore, snapshotCache, stateStore);
      }

      const apiMatch = url.pathname.match(/^\/api\/([^/]+)\/(data|discovery)$/);
      if (apiMatch) {
        return handleSourceApi(apiMatch[1], apiMatch[2], { config, registry, tokenStore });
      }

      return new Response(renderDashboard(await cachedSnapshot({ config, registry, tokenStore, snapshotCache })), {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store"
        }
      });
    }
  };
}

async function handleCallback(url, tokenStore, snapshotCache, stateStore) {
  const code = url.searchParams.get("code");
  const resolved = stateStore.consume(url.searchParams.get("state"));

  if (!resolved) return json({ status: "error", detail: "Invalid or missing OAuth state." }, 400);
  if (!code) return json({ status: "error", detail: "Missing OAuth code." }, 400);

  const source = resolved.source;

  const tokens = await exchangeCodeForTokens({
    code,
    env: process.env,
    redirectUri: process.env.GOOGLE_OAUTH_REDIRECT_URI || `${url.origin}/oauth/callback`
  });

  if (tokens.refresh_token) {
    await tokenStore.setRefreshToken(source, tokens.refresh_token);
    snapshotCache.clear();
  }

  return redirect("/");
}

async function handleSourceApi(source, action, ctx) {
  const connector = ctx.registry.get(source);
  if (!connector) return json({ status: "error", detail: "Unknown source." }, 404);

  const refreshToken = await ctx.tokenStore.getRefreshToken(source);
  if (!refreshToken) {
    return json({ status: "connect", detail: `Connect ${connector.label}.` });
  }

  try {
    if (action === "discovery") {
      const accessToken = await refreshAccessToken({ refreshToken, env: process.env });
      const all = await discoverGoogleSources({ accessToken, fetch: globalThis.fetch });
      return json({ status: "ok", options: all[source] || [] });
    }
    const metrics = await fetchSourceMetrics(source, { ...ctx, env: process.env, fetch: globalThis.fetch });
    return json({ status: "ok", metrics });
  } catch (error) {
    return json({ status: "error", detail: safeError(error) }, 502);
  }
}

function cachedSnapshot({ config, registry, tokenStore, snapshotCache }) {
  return snapshotCache.get(() => buildLiveSnapshot({
    config,
    registry,
    tokenStore,
    env: process.env,
    fetch: globalThis.fetch
  }));
}

function normalizeRoot(value) {
  if (value instanceof URL) return fileURLToPath(value);
  return String(value);
}

function json(value, status = 200) {
  return new Response(JSON.stringify(value, null, 2), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store"
    }
  });
}

function redirect(location) {
  return new Response(null, {
    status: 302,
    headers: { Location: location }
  });
}

function safeError(error) {
  const message = error?.message || String(error);
  return message.length > 180 ? `${message.slice(0, 177)}...` : message;
}
