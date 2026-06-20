import { getJson } from "./http.mjs";

export async function discoverGoogleSources({ accessToken, fetch = globalThis.fetch }) {
  const [ga4, gsc] = await Promise.all([
    discoverGa4Properties({ accessToken, fetch }),
    discoverSearchConsoleSites({ accessToken, fetch })
  ]);
  return { ga4, gsc };
}

export async function discoverGa4Properties({ accessToken, fetch = globalThis.fetch }) {
  const options = [];
  const seen = new Set();
  let pageToken = "";

  do {
    const url = new URL("https://analyticsadmin.googleapis.com/v1beta/accountSummaries");
    url.searchParams.set("pageSize", "200");
    if (pageToken) url.searchParams.set("pageToken", pageToken);
    const data = await getJson(url.toString(), accessToken, fetch);

    for (const property of propertySummaries(data)) {
      const rawId = property.property || "";
      if (!rawId || seen.has(rawId)) continue;
      seen.add(rawId);
      options.push({
        id: rawId.split("/").pop() || rawId,
        label: property.displayName || rawId,
        rawId
      });
    }

    pageToken = data.nextPageToken || "";
  } while (pageToken);

  return options;
}

function propertySummaries(data) {
  return [
    ...(data.propertySummaries || []),
    ...(data.accountSummaries || []).flatMap((account) => account.propertySummaries || [])
  ];
}

export async function discoverSearchConsoleSites({ accessToken, fetch = globalThis.fetch }) {
  const data = await getJson("https://searchconsole.googleapis.com/webmasters/v3/sites", accessToken, fetch);
  return (data.siteEntry || []).map((site) => ({
    id: site.siteUrl,
    label: site.siteUrl,
    permissionLevel: site.permissionLevel || ""
  }));
}
