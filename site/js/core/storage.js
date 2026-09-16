const memory = new Map();

export function get(key, fallback = null) {
  try {
    const value = localStorage.getItem(key);
    return value === null ? (memory.has(key) ? memory.get(key) : fallback) : value;
  } catch {
    return memory.has(key) ? memory.get(key) : fallback;
  }
}

export function set(key, value) {
  const text = String(value);
  try { localStorage.setItem(key, text); } catch { memory.set(key, text); }
  return true;
}

export function remove(key) {
  try { localStorage.removeItem(key); } catch {}
  memory.delete(key);
  return true;
}

export function jsonGet(key, fallback) {
  try {
    const raw = get(key, null);
    return raw === null ? fallback : JSON.parse(raw);
  } catch { return fallback; }
}

export function jsonSet(key, value) { return set(key, JSON.stringify(value)); }

export const Storage = { get, set, remove, jsonGet, jsonSet };
