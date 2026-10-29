import type {
  EligibilityFacts,
  EligibilityResponse,
  Player,
  SearchFilters,
  SimilarityResult,
} from "./types";

const BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? "/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    throw new ApiError(res.status, `${res.status} ${res.statusText} for ${path}`);
  }
  return res.json() as Promise<T>;
}

export function searchPlayers(filters: SearchFilters): Promise<Player[]> {
  const params = new URLSearchParams();
  if (filters.dataset) params.set("dataset", filters.dataset);
  if (filters.q) params.set("q", filters.q);
  if (filters.sort) params.set("sort", filters.sort);
  if (filters.eligibility_status) params.set("eligibility_status", filters.eligibility_status);
  if (filters.max_age != null) params.set("max_age", String(filters.max_age));
  if (filters.position) params.set("position", filters.position);
  if (filters.strong_foot) params.set("strong_foot", filters.strong_foot);
  if (filters.max_value_eur != null) params.set("max_value_eur", String(filters.max_value_eur));
  if (filters.diaspora_eligible != null)
    params.set("diaspora_eligible", String(filters.diaspora_eligible));

  const qs = params.toString();
  return request<Player[]>(`/players${qs ? `?${qs}` : ""}`);
}

export function getPlayer(id: string): Promise<Player> {
  return request<Player>(`/players/${encodeURIComponent(id)}`);
}

export async function downloadReport(id: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/players/${encodeURIComponent(id)}/report.pdf`);
  if (!res.ok) throw new ApiError(res.status, "Report could not be downloaded");
  const url = URL.createObjectURL(await res.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = `${id.replace(/[^a-zA-Z0-9_-]/g, "-").slice(0, 80)}-scout-report.pdf`;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export function getSimilarPlayers(id: string, topK = 5): Promise<SimilarityResult[]> {
  return request<SimilarityResult[]>(`/players/${encodeURIComponent(id)}/similar?top_k=${topK}`);
}

export function evaluateEligibility(
  playerId: string,
  facts: EligibilityFacts,
): Promise<EligibilityResponse> {
  return request<EligibilityResponse>(`/players/${encodeURIComponent(playerId)}/eligibility`, {
    method: "POST",
    body: JSON.stringify(facts),
  });
}
