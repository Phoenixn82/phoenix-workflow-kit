import { readFile, readdir, stat } from "node:fs/promises";
import { join } from "node:path";

export async function loadConfig(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

export async function loadEnvFiles(projectRoot, env = process.env) {
  for (const filename of [".env", ".env.local"]) {
    const path = join(projectRoot, filename);
    try {
      const info = await stat(path);
      if (info.isFile()) {
        await loadEnvFile(path, env);
        continue;
      }
      if (info.isDirectory()) {
        const entries = await readdir(path, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isFile()) await loadEnvFile(join(path, entry.name), env);
        }
      }
    } catch {
      // Local env files are optional and must never be logged.
    }
  }
  return env;
}

async function loadEnvFile(path, env) {
  const contents = await readFile(path, "utf8");
  for (const line of contents.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const index = trimmed.indexOf("=");
    if (index === -1) continue;
    const key = trimmed.slice(0, index).trim();
    const rawValue = trimmed.slice(index + 1).trim();
    if (key && !env[key]) env[key] = stripQuotes(rawValue);
  }
}

export function stripQuotes(value) {
  if ((value.startsWith("\"") && value.endsWith("\"")) || (value.startsWith("'") && value.endsWith("'"))) {
    return value.slice(1, -1);
  }
  return value;
}
