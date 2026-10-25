import { useEffect, useState } from "react";
import { searchPlayers } from "../api/client";
import type { Player, SearchFilters } from "../api/types";
import { FilterBar } from "../components/FilterBar";
import { PlayerCard } from "../components/PlayerCard";

export function SearchPage() {
  const [filters, setFilters] = useState<SearchFilters>({});
  const [players, setPlayers] = useState<Player[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    searchPlayers(filters)
      .then((result) => {
        if (!cancelled) setPlayers(result);
      })
      .catch(() => {
        if (!cancelled) setError("Couldn't reach the player database.");
      });
    return () => {
      cancelled = true;
    };
  }, [filters]);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">Player pool</h1>
        <p className="mt-1 text-sm text-ink-muted">
          {players ? `${players.length} players` : "Loading…"}
        </p>
      </div>

      <FilterBar filters={filters} onChange={setFilters} />

      {error && (
        <p className="rounded-[6px] border border-ineligible/30 bg-ineligible/10 px-4 py-3 text-sm text-ineligible">
          {error}
        </p>
      )}

      {players && players.length === 0 && !error && (
        <div className="rounded-[6px] border border-dashed border-border py-16 text-center">
          <p className="text-sm text-ink-muted">No players match these filters.</p>
        </div>
      )}

      {players && players.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {players.map((player) => (
            <PlayerCard key={player.id} player={player} />
          ))}
        </div>
      )}
    </div>
  );
}
