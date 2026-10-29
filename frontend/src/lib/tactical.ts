import { TACTICAL_METRICS, type Player } from "../api/types.ts";
const aliases: Record<string, string> = {
  Goalkeeper: "GK",
  "Centre-Back": "CB",
  "Center-Back": "CB",
  "Defensive Midfielder": "DM",
  Midfielder: "CM",
  Forward: "ST",
  CF: "ST",
  Striker: "ST",
};
export function roles(position: string | null): string[] {
  return (position ?? "")
    .split("/")
    .map((p) => aliases[p.trim()] ?? p.trim())
    .filter(Boolean);
}
function league(player: Player) {
  return player.league_band?.split(" -- ")[0].trim();
}
export function tacticalComparison(player: Player, pool: Player[]) {
  if (TACTICAL_METRICS.some((metric) => player[metric] == null)) return null;
  const position = roles(player.position);
  const peers = pool.filter(
    (p) =>
      p.id !== player.id &&
      p.id.startsWith("synthetic-v1-") === player.id.startsWith("synthetic-v1-") &&
      league(p) &&
      league(p) === league(player) &&
      roles(p.position).some((role) => position.includes(role)) &&
      TACTICAL_METRICS.every((metric) => p[metric] != null),
  );
  if (!peers.length) return null;
  const cohort = [...peers, player];
  const data = TACTICAL_METRICS.map((metric) => {
    const values = cohort.map((p) => p[metric] as number).sort((a, b) => a - b);
    const middle = Math.floor(values.length / 2);
    const median = values.length % 2 ? values[middle] : (values[middle - 1] + values[middle]) / 2;
    const percentile = (value: number) =>
      (100 *
        (values.filter((v) => v < value).length + values.filter((v) => v === value).length / 2)) /
      values.length;
    return { metric, player: percentile(player[metric] as number), median: percentile(median) };
  });
  return { data, count: cohort.length };
}
