import assert from "node:assert/strict";
import test from "node:test";
import { assertFreeEndpoint, isEndpointAllowed } from "../engine/free-only-guard.mjs";

test("free-only guard allows included account APIs and blocks paid or unknown-cost endpoints", () => {
  assert.equal(isEndpointAllowed({
    id: "ga4",
    currentTier: "included_account_api",
    cost: "free_google_account_quota"
  }).allowed, true);

  assert.throws(() => assertFreeEndpoint({
    id: "paid",
    currentTier: "paid_api",
    cost: "paid_api"
  }), /Blocked.*paid_api/);

  assert.throws(() => assertFreeEndpoint({
    id: "unknown",
    currentTier: "included_account_api",
    cost: "unknown_cost_api"
  }), /Blocked.*unknown_cost_api/);
});
