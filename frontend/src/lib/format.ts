export function formatValue(eur: number | null | undefined): string {
  if (eur == null) return "—";
  if (eur >= 1_000_000) return `€${(eur / 1_000_000).toFixed(1)}M`;
  if (eur >= 1_000) return `€${(eur / 1_000).toFixed(0)}K`;
  return `€${eur}`;
}

export function formatMetric(value: number | null | undefined): string {
  return value == null ? "—" : value.toFixed(2);
}

export function formatReferenceMetric(key: string, value: number | null | undefined): string {
  if (value == null) return "—";
  if (key === "minutes_played" || key === "appearances") return value.toLocaleString();
  if (key === "shot_accuracy_pct" || key === "pass_completion_pct") return `${value.toFixed(1)}%`;
  return value.toFixed(2);
}
