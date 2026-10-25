import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts";
import type { Player, TacticalMetric } from "../api/types";
import { METRIC_LABELS, TACTICAL_METRICS } from "../api/types";

interface Props {
  player: Player;
  pool: Player[];
}

function poolAverage(pool: Player[], metric: TacticalMetric): number {
  const values = pool
    .map((p) => p[metric])
    .filter((v): v is number => v != null);
  if (values.length === 0) return 0;
  return values.reduce((sum, v) => sum + v, 0) / values.length;
}

export function TacticalRadar({ player, pool }: Props) {
  const hasAnyMetric = TACTICAL_METRICS.some((m) => player[m] != null);

  if (!hasAnyMetric) {
    return (
      <div className="flex h-72 flex-col items-center justify-center gap-2 rounded-[6px] border border-dashed border-border text-center">
        <p className="text-sm font-medium text-ink-muted">No tactical data available</p>
        <p className="max-w-xs text-xs text-ink-faint">
          This player has no recorded per-90 metrics yet — common for players outside
          FBref's tracked competitions.
        </p>
      </div>
    );
  }

  const data = TACTICAL_METRICS.map((metric) => ({
    metric: METRIC_LABELS[metric],
    player: player[metric] ?? 0,
    pool: poolAverage(pool, metric),
  }));

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        {/* Signature move: the radar's background grid reads as a pitch's
            concentric center-circle rings, in the pitch-green accent --
            not a generic grey polygon grid. */}
        <RadarChart data={data} outerRadius="72%">
          <PolarGrid gridType="circle" stroke="#22c55e" strokeOpacity={0.18} />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "#9aa5b1", fontSize: 11 }}
          />
          <PolarRadiusAxis tick={false} axisLine={false} />
          <Radar
            name="Pool average"
            dataKey="pool"
            stroke="#5b6673"
            fill="#5b6673"
            fillOpacity={0.15}
          />
          <Radar
            name={player.name}
            dataKey="player"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.35}
          />
        </RadarChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center justify-center gap-6 text-xs text-ink-muted">
        <Legend color="#22c55e" label={player.name} />
        <Legend color="#5b6673" label="Pool average (approximation)" />
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <span className="flex items-center gap-1.5">
      <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
      {label}
    </span>
  );
}
