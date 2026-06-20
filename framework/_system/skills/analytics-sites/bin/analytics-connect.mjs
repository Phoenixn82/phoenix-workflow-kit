#!/usr/bin/env node
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { loadEnvFiles } from "../engine/config.mjs";
import { assertFreeEndpoint, isEndpointAllowed } from "../engine/free-only-guard.mjs";
import { createConnectorRegistry } from "../engine/registry.mjs";
import { buildLiveSnapshot } from "../engine/snapshot.mjs";
import { LocalFileTokenStore } from "../engine/token-store.mjs";
import registry from "../connectors/source-registry.json" with { type: "json" };

const command = process.argv[2] || "help";
const args = process.argv.slice(3);

if (command === "help" || command === "--help" || command === "-h") {
  help();
} else if (command === "sync") {
  await sync();
} else if (command === "policy") {
  console.log(JSON.stringify(registry, null, 2));
} else if (command === "guard") {
  guard();
} else {
  console.error(`Unknown command: ${command}`);
  help();
  process.exitCode = 2;
}

async function sync() {
  const configPath = valueAfter("--config") || "company.config.json";
  const resolvedConfigPath = resolve(configPath);
  const projectRoot = dirname(resolvedConfigPath);
  const outPath = resolve(valueAfter("--out") || join(projectRoot, "src", "analytics-snapshot.json"));
  const config = JSON.parse(await readFile(resolvedConfigPath, "utf8"));

  await loadEnvFiles(projectRoot, process.env);
  for (const id of config.cards || registry.sources.map((source) => source.id)) {
    const source = registry.sources.find((item) => item.id === id);
    const guard = isEndpointAllowed(source, registry.policy);
    if (!guard.allowed) {
      throw new Error(`${id} blocked by free-only guard: ${guard.reason}`);
    }
  }

  const snapshot = await buildLiveSnapshot({
    config,
    registry: createConnectorRegistry(),
    tokenStore: new LocalFileTokenStore(join(projectRoot, ".analytics-sites", "tokens.json")),
    env: process.env,
    fetch: globalThis.fetch
  });

  await mkdir(dirname(outPath), { recursive: true });
  await writeFile(outPath, `${JSON.stringify(snapshot, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({
    status: "ok",
    output: outPath,
    connectedSources: snapshot.summary.connectedSources,
    sources: snapshot.sources.map((source) => ({
      id: source.id,
      status: source.status,
      detail: source.detail
    }))
  }, null, 2));
}

function guard() {
  const currentTier = valueAfter("--tier") || "";
  const cost = valueAfter("--cost") || "";
  try {
    assertFreeEndpoint({ id: "cli-check", currentTier, cost }, registry.policy);
    console.log("allowed");
  } catch (error) {
    console.error(error.message);
    process.exitCode = 2;
  }
}

function valueAfter(name) {
  const index = args.indexOf(name);
  return index === -1 ? "" : args[index + 1] || "";
}

function help() {
  console.log(`Analytics Sites CLI

Usage:
  analytics-connect sync --config company.config.json
  analytics-connect policy
  analytics-connect guard --tier included_account_api --cost free_google_account_quota
`);
}
