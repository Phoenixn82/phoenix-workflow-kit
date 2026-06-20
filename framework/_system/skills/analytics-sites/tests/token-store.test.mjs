import assert from "node:assert/strict";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";
import { LocalFileTokenStore } from "../engine/token-store.mjs";

test("local token store round-trips a fake refresh token", async () => {
  const dir = await mkdtemp(join(tmpdir(), "analytics-sites-"));
  try {
    const store = new LocalFileTokenStore(join(dir, "tokens.json"));
    await store.setRefreshToken("ga4", "fake-refresh-token");
    assert.equal(await store.getRefreshToken("ga4"), "fake-refresh-token");
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
});
