const ROOT = `${import.meta.env.VITE_API_URL || "/api/v1"}/investscan`;
let csrf = "";
export function setCsrf(value) {
  csrf = value || "";
}
export async function request(path, options = {}) {
  const { headers, ...rest } = options;
  const response = await fetch(ROOT + path, {
    credentials: "same-origin",
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(csrf ? { "X-CSRF-Token": csrf } : {}),
      ...headers,
    },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail)
      ? data.detail
          .map((x) => `${x.loc?.slice(1).join(".")}: ${x.msg}`)
          .join("; ")
      : data.detail;
    const error = new Error(detail || `Ошибка запроса (${response.status})`);
    error.status = response.status;
    if (response.status === 401)
      window.dispatchEvent(new Event("investscan-session-expired"));
    throw error;
  }
  return response.status === 204 ? null : response.json();
}
export const send = (path, body, method = "POST") =>
  request(path, { method, body: JSON.stringify(body) });
export const loginUrl = (next) =>
  ROOT + "/auth/login?next=" + encodeURIComponent(next);
export function queryString(filters) {
  return new URLSearchParams(
    Object.fromEntries(
      Object.entries(filters).filter(
        ([, v]) => v !== "" && v != null && v !== false,
      ),
    ),
  ).toString();
}
