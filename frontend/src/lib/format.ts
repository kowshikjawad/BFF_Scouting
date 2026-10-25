export function formatValue(eur: number | null | undefined): string {
  if (eur == null) return "—";
  if (eur >= 1_000_000) return `€${(eur / 1_000_000).toFixed(1)}M`;
  if (eur >= 1_000) return `€${(eur / 1_000).toFixed(0)}K`;
  return `€${eur}`;
}

export function formatMetric(value: number | null | undefined): string {
  return value == null ? "—" : value.toFixed(2);
}
