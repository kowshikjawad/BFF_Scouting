import { Link, useLocation } from "react-router-dom";
import { ArrowUpRight, MapPin } from "lucide-react";
import type { Player } from "../api/types";
import { Avatar } from "./Avatar";
import { EligibilityPill } from "./EligibilityPill";
import { SaveButton } from "./SaveButton";
import { formatValue } from "../lib/format";
export function PlayerCard({ player }: { player: Player }) {
  const location = useLocation();
  const name = player.name ?? player.id;
  return (
    <article className="panel panel-interactive p-5 transition-colors hover:border-pitch/40">
      <div className="mb-5 flex items-center justify-between">
        <Avatar id={player.id} name={name} size={44} />
        <SaveButton id={player.id} name={name} />
      </div>
      <Link
        to={`/players/${encodeURIComponent(player.id)}`}
        state={{ from: location.pathname + location.search }}
        className="player-name flex items-center gap-2 font-display text-base"
      >
        {name}
        <ArrowUpRight size={14} className="ml-auto shrink-0 text-ink-faint" />
      </Link>
      <p className="mt-2 flex items-start gap-1.5 text-[11px] leading-relaxed text-ink-muted">
        <MapPin size={12} className="mt-0.5 shrink-0" />
        {player.league_band ?? "League not recorded"}
      </p>
      <dl className="my-5 grid grid-cols-3 gap-2 border-y border-border py-4">
        <div>
          <dt className="text-[10px] text-ink-muted">Position</dt>
          <dd className="mt-1 text-xs font-medium">{player.position ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-[10px] text-ink-muted">Age</dt>
          <dd className="mt-1 text-xs font-medium">{player.age ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-[10px] text-ink-muted">Est. value</dt>
          <dd className="mt-1 text-xs font-medium">{formatValue(player.estimated_value_eur)}</dd>
        </div>
      </dl>
      <div className="flex items-center justify-between gap-2">
        <EligibilityPill status={player.ancestry_eligibility} />
        <span className="text-[10px] text-ink-muted">
          {player.strong_foot ? `${player.strong_foot} foot` : "Foot unknown"}
        </span>
      </div>
    </article>
  );
}
