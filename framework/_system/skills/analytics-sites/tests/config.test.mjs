import assert from "node:assert/strict";
import { mkdir, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { loadEnvFiles } from "../engine/config.mjs";

test("loadEnvFiles supports a .env.local directory without logging secrets", async () => {
  const dir = await mkdtemp(join(tmpdir(), "analytics-sites-env-"));
  try {
    const envDir = join(dir, ".env.local");
    await mkdir(envDir);
    await writeFile(join(envDir, "New Text Document.txt"), "GOOGLE_OAUTH_CLIENT_ID=fake-client\n", "utf8");

    const env = {};
    await loadEnvFiles(dir, env);

    assert.equal(env.GOOGLE_OAUTH_CLIENT_ID, "fake-client");
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});
