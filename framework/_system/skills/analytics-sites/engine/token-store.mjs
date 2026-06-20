import { mkdir, open, readFile, rename } from "node:fs/promises";
import { dirname } from "node:path";

export class LocalFileTokenStore {
  constructor(path) {
    this.path = path;
  }

  async getRefreshToken(source) {
    const data = await this.#read();
    return data.tokens?.[source]?.refreshToken || "";
  }

  async setRefreshToken(source, refreshToken) {
    const data = await this.#read();
    data.tokens = data.tokens || {};
    data.tokens[source] = {
      refreshToken,
      updatedAt: new Date().toISOString()
    };
    await atomicWriteJson(this.path, data);
  }

  async #read() {
    try {
      return JSON.parse(await readFile(this.path, "utf8"));
    } catch {
      return { tokens: {} };
    }
  }
}

export class SitesNativeTokenStore {
  constructor(env = process.env) {
    this.env = env;
  }

  async getRefreshToken(source) {
    const key = `ANALYTICS_REFRESH_TOKEN_${String(source).toUpperCase()}`;
    return this.env[key] || "";
  }

  async setRefreshToken() {
    throw new Error("Sites-native writable token storage is not configured. Save the refresh token as a Sites secret.");
  }
}

export async function atomicWriteJson(path, value) {
  await mkdir(dirname(path), { recursive: true });
  const tempPath = `${path}.${process.pid}.${Date.now()}.tmp`;
  const handle = await open(tempPath, "w");
  try {
    await handle.writeFile(`${JSON.stringify(value, null, 2)}\n`, "utf8");
    await handle.sync();
  } finally {
    await handle.close();
  }
  await rename(tempPath, path);
}
