import registry from "../connectors/source-registry.json" with { type: "json" };
import { createGa4Connector } from "../connectors/ga4.mjs";
import { createGscConnector } from "../connectors/gsc.mjs";
import { createPlaceholderConnector } from "../connectors/placeholder.mjs";

export function createConnectorRegistry() {
  const connectors = new Map();
  connectors.set("ga4", createGa4Connector());
  connectors.set("gsc", createGscConnector());

  for (const source of registry.sources) {
    if (!connectors.has(source.id)) {
      connectors.set(source.id, createPlaceholderConnector(source));
    }
  }

  return {
    policy: registry.policy,
    sourceRegistry: registry.sources,
    connectors,
    get(id) {
      return connectors.get(id);
    }
  };
}
