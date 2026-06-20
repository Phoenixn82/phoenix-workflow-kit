export function createPlaceholderConnector({ id, label }) {
  return {
    id,
    label,
    auth: { type: "none", scopes: [] },
    connectUrl: () => `/connect/${id}`,
    isConnected: () => false,
    fetch: async () => [],
    healthcheck: async () => ({
      status: "connect",
      detail: `Connect ${label}.`
    })
  };
}
