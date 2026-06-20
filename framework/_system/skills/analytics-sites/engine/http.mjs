export async function postJson(url, accessToken, body, fetchImpl = globalThis.fetch) {
  const response = await fetchImpl(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(body)
  });
  return parseJsonResponse(response);
}

export async function getJson(url, accessToken, fetchImpl = globalThis.fetch) {
  const response = await fetchImpl(url, {
    headers: {
      Authorization: `Bearer ${accessToken}`
    }
  });
  return parseJsonResponse(response);
}

export async function postForm(url, values, fetchImpl = globalThis.fetch) {
  const response = await fetchImpl(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams(values)
  });
  return parseJsonResponse(response);
}

export async function parseJsonResponse(response) {
  const text = await response.text();
  let data = {};
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    data = { raw: text };
  }

  if (!response.ok) {
    const message = data.error?.message || data.message || response.statusText || "Request failed";
    throw new Error(`${response.status} ${message}`);
  }

  return data;
}
