import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { Activity } from "lucide-react";
import type { Player } from "../api/types";
import { METRIC_LABELS, TACTICAL_METRICS } from "../api/types";
import { tacticalComparison } from "../lib/tactical";
export function TacticalRadar({ player, pool }: { player: Player; pool: Player[] }) {
  const comparison = tacticalComparison(player, pool);
  const missing = TACTICAL_METRICS.some((m) => player[m] == null);
  if (!comparison)
    return (
      <div className="flex min-h-64 flex-col items-center justify-center rounded-panel border border-dashed border-border bg-shell/50 px-7 text-center">
        <span className="mb-3 rounded-full bg-pitch-tint p-3 text-pitch">
          <Activity size={22} strokeWidth={1.5} />
        </span>
        <p className="text-sm font-medium">
          {missing ? "Tactical data is still taking shape" : "No comparable cohort available"}
        </p>
        <p className="mt-2 max-w-sm text-xs leading-relaxed text-ink-muted">
          {missing
            ? "A complete set of per-90 metrics is needed to draw a reliable profile. Available recorded values are shown below."
            : "A comparison needs players in the same league and position with complete metrics. This player’s recorded values are shown below."}
        </p>
      </div>
    );
  const data = comparison.data.map((row) => ({ ...row, metric: METRIC_LABELS[row.metric] }));
  return (
    <div>
      <div
        className="h-72"
        role="img"
        aria-label={`Tactical percentile comparison of ${player.name ?? player.id} against ${comparison.count} players in the same league and position`}
      >
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} outerRadius="68%">
            <PolarGrid stroke="var(--color-chart-grid)" />
            <PolarAngleAxis
              dataKey="metric"
              tick={{ fill: "var(--color-ink-muted)", fontSize: 10 }}
            />
            <PolarRadiusAxis
              domain={[0, 100]}
              ticks={[25, 50, 75, 100]}
              tick={false}
              axisLine={false}
            />
            <Tooltip formatter={(v) => `${Number(v).toFixed(0)}th percentile`} />
            <Radar
              name="Cohort median"
              dataKey="median"
              stroke="var(--color-chart-cohort)"
              fill="var(--color-chart-cohort)"
              fillOpacity={0.12}
            />
            <Radar
              name={player.name ?? player.id}
              dataKey="player"
              stroke="var(--color-pitch)"
              fill="var(--color-pitch)"
              fillOpacity={0.2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex justify-center gap-5 text-[10px] text-ink-muted">
        <span>
          <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-pitch" />
          Player
        </span>
        <span>
          <span className="mr-1.5 inline-block h-2 w-2 rounded-full bg-[var(--color-chart-cohort)]" />
          Cohort median
        </span>
      </div>
      <p className="mt-3 text-center text-[10px] text-ink-muted">
        Percentile scale · {comparison.count} players · same league & position
      </p>
    </div>
  );
}
