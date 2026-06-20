import sourceRegistry from "../connectors/source-registry.json" with { type: "json" };

// Single source of truth: the per-fetch guard and the CLI pre-check both read
// the policy declared in connectors/source-registry.json (see registry.mjs),
// so they can never diverge.
export const FREE_ONLY_POLICY = sourceRegistry.policy;

export function isEndpointAllowed(endpoint, policy = FREE_ONLY_POLICY) {
  if (!endpoint || typeof endpoint !== "object") {
    return { allowed: false, reason: "Blocked: endpoint is not registered in the free-only policy." };
  }

  const tier = String(endpoint.currentTier || endpoint.preferredTier || "");
  const cost = String(endpoint.cost || "");
  const blocked = new Set(policy.blocked || []);

  for (const value of [tier, cost]) {
    for (const blockedValue of blocked) {
      if (value === blockedValue || value.includes(blockedValue)) {
        return { allowed: false, reason: `Blocked: ${blockedValue} is not allowed by the free-only guard.` };
      }
    }
  }

  if (!cost || /paid|metered|unknown/i.test(cost)) {
    return { allowed: false, reason: `Blocked: ${cost || "unknown_cost_api"} is not allowed by the free-only guard.` };
  }

  const hasAllowedTier = (policy.tierOrder || []).some((allowedTier) => tier.includes(allowedTier));
  const hasFreeCost = /free|included|local|existing/i.test(cost);

  if (!hasAllowedTier || !hasFreeCost) {
    return { allowed: false, reason: `Blocked: ${endpoint.id || "endpoint"} is not proven free.` };
  }

  return { allowed: true, reason: "Allowed by free-only guard." };
}

export function assertFreeEndpoint(endpoint, policy = FREE_ONLY_POLICY) {
  const result = isEndpointAllowed(endpoint, policy);
  if (!result.allowed) {
    throw new Error(result.reason);
  }
  return endpoint;
}
