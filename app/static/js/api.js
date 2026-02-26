const API_BASE = "http://localhost:5000/api";

async function fetchMenu() {
  const res = await fetch(`${API_BASE}/menu`);
  return await res.json();
}
