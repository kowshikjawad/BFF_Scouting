import { Link } from "react-router-dom";
import type { Player } from "../api/types";
import { Avatar } from "./Avatar";
import { EligibilityPill } from "./EligibilityPill";
import { formatValue } from "../lib/format";

export function PlayerCard({ player }: { player: Player }) {
  return (
    <Link
      to={`/players/${player.id}`}
      className="group flex flex-col gap-3 rounded-[6px] border border-border bg-surface p-4 transition-colors hover:border-pitch/60"
    >
      <div className="flex items-start gap-3">
        <Avatar id={player.id} name={player.name} />
        <div className="min-w-0 flex-1">
          <p className="truncate font-display text-sm font-semibold text-ink group-hover:text-pitch">
            {player.name}
          </p>
          <p className="truncate text-xs text-ink-muted">{player.league_band}</p>
        </div>
      </div>

      <div className="flex items-center justify-between text-xs text-ink-muted">
        <span>{player.age != null ? `${player.age} yrs` : "Age —"}</span>
        <span className="rounded-[6px] border border-border-strong px-1.5 py-0.5 font-medium text-ink">
          {player.position}
        </span>
        <span>{formatValue(player.estimated_value_eur)}</span>
      </div>

      <div className="flex items-center justify-between">
        <EligibilityPill status={player.ancestry_eligibility} />
        {player.strong_foot && (
          <span className="text-xs text-ink-faint">{player.strong_foot} foot</span>
        )}
      </div>
    </Link>
  );
}
