const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export const USE_FIXTURES = import.meta.env.VITE_USE_FIXTURES === 'true';

export class ApiError extends Error {
  status: number;
  statusText: string;

  constructor(status: number, statusText: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

export async function apiFetch<T>(
  path: string,
  params?: Record<string, string | string[] | undefined>
): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value === undefined) continue;
      if (Array.isArray(value)) {
        value.forEach((v) => url.searchParams.append(key, v));
      } else {
        url.searchParams.set(key, value);
      }
    }
  }

  const res = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
  });

  if (!res.ok) {
    throw new ApiError(res.status, res.statusText, await res.text());
  }

  return res.json() as Promise<T>;
}
