interface CustomOptions {
  query?: Record<string, any>;
  token?: string;
  body?: Record<string, any>;
  method?: string;
}

const isServer = typeof window === "undefined";
export const API_URL = isServer
  ? process.env.NEXT_API_URL || process.env.NEXT_PUBLIC_API_URL
  : process.env.NEXT_PUBLIC_API_URL;
export const cachePolicy = process.env.NEXT_PUBLIC_CACHE_POLICY;

export const getCachePolicy = () => {
  switch (cachePolicy) {
    case "no-cache":
      return "no-cache";
    case "cache":
      return "default";
    case "cache-first":
      return "default";
    case "network-only":
      return "no-store";
    default:
      return "default";
  }
};

export async function customFetch(url: string, options?: CustomOptions): Promise<Response> {
  const params = new URLSearchParams();

  const appendParams = (key: string, value: any) => {
    if (typeof value === "object" && !Array.isArray(value)) {
      for (const subKey in value) {
        appendParams(`${key}`, value[subKey]);
      }
    } else if (Array.isArray(value)) {
      value.forEach((item) => {
        params.append(`${key}`, item);
      });
    } else {
      if (value !== undefined) {
        params.append(key, value);
      }
    }
  };

  if (!options) {
    options = {};
  }

  for (const key in options["query"]) {
    appendParams(key, options["query"][key]);
  }

  const urlWithParams = `${API_URL}/${url}?${params.toString()}`;

  let response;
  try {
    response = await fetch(urlWithParams, {
      cache: getCachePolicy(),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${options.token}`
      },
      body: JSON.stringify(options.body),
      method: options.method || "GET"
    });
  } catch (err: any) {
    const networkMsg = `Network error fetching ${urlWithParams}: ${err?.message || String(err)}`;
    console.error(networkMsg, err);
    throw new Error(networkMsg);
  }

  if (!response.ok) {
    let msg = `API error ${response.status} on ${urlWithParams}`;
    try {
      const body = await response.json();
      if (body.message) {
        msg += `: ${body.message}`;
      } else if (body.detail?.[0]?.msg) {
        msg += `: ${body.detail[0].msg}`;
      } else if (body.detail) {
        msg += `: ${typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail)}`;
      }
    } catch { /* ignore parse errors */ }
    console.error(msg);
    throw new Error(msg);
  }

  return response;
}
