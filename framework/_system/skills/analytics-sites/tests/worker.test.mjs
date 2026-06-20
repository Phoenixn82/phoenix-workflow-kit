import assert from "node:assert/strict";
import { mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test, { after, before } from "node:test";
import { createWorker } from "../engine/worker.mjs";

let projectRoot;
let worker;

before(async () => {
  projectRoot = await mkdtemp(join(tmpdir(), "analytics-sites-worker-"));
  await writeFile(
    join(projectRoot, "company.config.json"),
    JSON.stringify({ company: { name: "Test Co" }, sources: {}, cards: [] }),
    "utf8"
  );
  worker = await createWorker({
    projectRoot,
    env: {},
    tokenStore: {
      async getRefreshToken() {
        return "";
      },
      async setRefreshToken() {}
    }
  });
});

after(async () => {
  if (projectRoot) await rm(projectRoot, { recursive: true, force: true });
});

test("OAuth callback rejects a missing state instead of defaulting to ga4", async () => {
  const response = await worker.fetch(new Request("http://localhost:8787/oauth/callback?code=abc"));
  assert.equal(response.status, 400);
  const body = await response.json();
  assert.equal(body.status, "error");
  assert.match(body.detail, /state/i);
});

test("OAuth callback rejects an unrecognized state even when a code is present", async () => {
  const response = await worker.fetch(
    new Request("http://localhost:8787/oauth/callback?code=abc&state=garbage")
  );
  assert.equal(response.status, 400);
  const body = await response.json();
  assert.match(body.detail, /state/i);
});

test("/connect rejects a non-OAuth placeholder source instead of minting a Google token", async () => {
  const response = await worker.fetch(new Request("http://localhost:8787/connect/vercel"));
  assert.equal(response.status, 400);
  const body = await response.json();
  assert.equal(body.status, "error");
  assert.match(body.detail, /Google OAuth/i);
});

test("/connect/ga4 redirects to Google consent with that source's declared scope only", async () => {
  const response = await worker.fetch(new Request("http://localhost:8787/connect/ga4"));
  assert.equal(response.status, 302);
  const location = new URL(response.headers.get("Location"));
  assert.equal(location.origin + location.pathname, "https://accounts.google.com/o/oauth2/v2/auth");
  assert.equal(location.searchParams.get("scope"), "https://www.googleapis.com/auth/analytics.readonly");
  assert.ok(location.searchParams.get("state"), "consent URL carries a state nonce");
});
