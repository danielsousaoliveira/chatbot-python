export async function apiFetch<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, { ...init, credentials: 'include' })
  const data = await res.json()
  if (!res.ok) throw { status: res.status, detail: data.detail ?? 'An error occurred' }
  return data as T
}
