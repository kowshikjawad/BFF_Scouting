import { useSearchParams, Link, useLocation } from "react-router-dom";
import {
  ArrowDownUp,
  Bookmark,
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  List,
  Search,
  ShieldCheck,
  SlidersHorizontal,
  Users,
  X,
} from "lucide-react";
import { useState } from "react";
import { searchPlayers } from "../api/client";
import type { SearchFilters } from "../api/types";
import { useResource } from "../hooks/useResource";
import { useDataset, sourceFromId } from "../lib/dataset-context";
import { useShortlist } from "../lib/shortlist-context";
import { PlayerCard } from "../components/PlayerCard";
import { Avatar } from "../components/Avatar";
import { EligibilityPill } from "../components/EligibilityPill";
import { SaveButton } from "../components/SaveButton";
import { formatValue } from "../lib/format";

const PAGE_SIZE = 12;
export function SearchPage({ shortlist = false }: { shortlist?: boolean }) {
  const [params, setParams] = useSearchParams();
  const [filtersOpen, setFiltersOpen] = useState(false);
  const location = useLocation();
  const { ids, toggle } = useShortlist();
  const { dataset, pathFor } = useDataset();
  const visibleIds = ids.filter((id) => sourceFromId(id) === dataset);
  const filters: SearchFilters = { dataset };
  for (const key of ["q", "position", "strong_foot", "eligibility_status", "sort"] as const) {
    const value = params.get(key);
    if (value) Object.assign(filters, { [key]: value });
  }
  for (const key of ["max_age", "max_value_eur"] as const) {
    const value = params.get(key);
    if (value && Number.isFinite(Number(value))) filters[key] = Number(value);
  }
  const filterKey = JSON.stringify(filters);
  const result = useResource(filterKey, () => searchPlayers(filters));
  const inventory = useResource(`inventory:${dataset}`, () => searchPlayers({ dataset }));
  const players = (result.data ?? []).filter((player) => !shortlist || ids.includes(player.id));
  const all = inventory.data ?? [];
  const missing =
    shortlist && inventory.data ? visibleIds.filter((id) => !all.some((p) => p.id === id)) : [];
  const totalPages = Math.max(1, Math.ceil(players.length / PAGE_SIZE));
  const page = Math.min(totalPages, Math.max(1, Number.parseInt(params.get("page") ?? "1") || 1));
  const shown = players.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const cards = params.get("view") === "cards";
  const filterCount = Object.keys(filters).filter(
    (key) => key !== "sort" && key !== "q" && key !== "dataset",
  ).length;
  function update(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page" && key !== "view") next.delete("page");
    setParams(next, { replace: key === "q" });
  }
  function reset() {
    setParams(cards ? { view: "cards", dataset } : { dataset });
  }
  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="page-title">
            {shortlist ? "My shortlist" : "Player discovery"}
            <span className="text-pitch">.</span>
          </h1>
          <p className="page-description max-w-md">
            {shortlist
              ? "Keep promising players close. Pick up where your scouting left off."
              : "Explore domestic talent and Bangladeshi heritage across the world."}
          </p>
        </div>
        <Link to={pathFor(shortlist ? "/" : "/eligibility")} className="btn mt-1">
          {shortlist ? <Search size={15} /> : <ShieldCheck size={15} />}
          {shortlist ? "Discover players" : "Check eligibility"}
        </Link>
      </div>
      <div className="hero-band my-8 py-7">
        <img
          src="/accents/hero-pattern.webp"
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute inset-y-0 right-0 z-0 hidden h-full w-auto opacity-80 sm:block"
        />
        <div className="relative z-10 flex flex-wrap items-center gap-x-10 gap-y-6 px-7">
          <HeroStat
            label={shortlist ? "Saved players" : "Players in database"}
            value={shortlist ? visibleIds.length : inventory.data?.length}
          />
          <HeroStat
            label="Assessed players"
            value={inventory.data ? all.filter((p) => p.ancestry_eligibility).length : undefined}
          />
          <HeroStat
            label="Tactical coverage"
            value={
              inventory.data
                ? all.filter(
                    (p) =>
                      p.goals_per_90 != null ||
                      p.key_passes_per_90 != null ||
                      p.progressive_carries_per_90 != null ||
                      p.tackles_won_per_90 != null ||
                      p.aerial_duel_pct != null,
                  ).length
                : undefined
            }
          />
          <div className="ml-auto hidden max-w-48 items-center gap-3 text-[11px] leading-relaxed text-on-pitch-muted xl:flex">
            <Users size={22} className="shrink-0 text-on-pitch" />
            {dataset === "synthetic"
              ? "Fictional players. Complete metrics. Explore every workflow."
              : "Real profiles. A clearer picture of the player pool."}
          </div>
        </div>
      </div>
      {missing.length > 0 && (
        <div className="panel mb-5 p-4 text-xs text-ink-muted">
          <p className="mb-2">
            {missing.length} saved {missing.length === 1 ? "player is" : "players are"} no longer in
            the database.
          </p>
          {missing.map((id) => (
            <button key={id} onClick={() => toggle(id)} className="btn mr-2 mt-2">
              Remove {id}
              <X size={12} />
            </button>
          ))}
        </div>
      )}
      <section className="panel overflow-hidden" aria-label="Player directory">
        <div className="flex flex-wrap items-center gap-3 border-b border-border p-4 sm:px-5">
          <div className="relative min-w-44 flex-1">
            <Search
              size={16}
              className="pointer-events-none absolute left-3 top-3 text-ink-muted"
            />
            <input
              aria-label="Search players by name"
              type="search"
              placeholder="Search players by name…"
              maxLength={100}
              value={params.get("q") ?? ""}
              onChange={(e) => update("q", e.target.value)}
              className="w-full pl-9!"
            />
          </div>
          <button
            className={`btn ${filterCount ? "border-pitch! text-pitch" : ""}`}
            onClick={() => setFiltersOpen((v) => !v)}
            aria-expanded={filtersOpen}
            aria-controls="player-filters"
          >
            <SlidersHorizontal size={14} />
            Filters
            {filterCount > 0 && (
              <span className="rounded bg-pitch px-1.5 text-[10px] text-white">{filterCount}</span>
            )}
          </button>
          <div className="flex rounded-control border border-border p-0.5">
            <button
              aria-label="Table view"
              aria-pressed={!cards}
              className={`icon-button h-8! w-8! ${!cards ? "bg-pitch-tint text-pitch!" : ""}`}
              onClick={() => update("view", "")}
            >
              <List size={16} />
            </button>
            <button
              aria-label="Card view"
              aria-pressed={cards}
              className={`icon-button h-8! w-8! ${cards ? "bg-pitch-tint text-pitch!" : ""}`}
              onClick={() => update("view", "cards")}
            >
              <LayoutGrid size={15} />
            </button>
          </div>
        </div>
        {filtersOpen && (
          <div
            id="player-filters"
            className="grid grid-cols-2 gap-4 border-b border-border bg-[var(--color-table-head)] p-5 md:grid-cols-3 xl:grid-cols-5"
          >
            <Filter label="Position">
              <select
                value={filters.position ?? ""}
                onChange={(e) => update("position", e.target.value)}
              >
                <option value="">All positions</option>
                {["GK", "CB", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "ST"].map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </Filter>
            <Filter label="Maximum age">
              <input
                type="number"
                min={0}
                max={100}
                placeholder="Any age"
                value={params.get("max_age") ?? ""}
                onChange={(e) => update("max_age", e.target.value)}
              />
            </Filter>
            <Filter label="Preferred foot">
              <select
                value={filters.strong_foot ?? ""}
                onChange={(e) => update("strong_foot", e.target.value)}
              >
                <option value="">Either foot</option>
                {["Left", "Right", "Both"].map((f) => (
                  <option key={f}>{f}</option>
                ))}
              </select>
            </Filter>
            <Filter label="Maximum value (€)">
              <input
                type="number"
                min={0}
                step={1000}
                placeholder="Any value"
                value={params.get("max_value_eur") ?? ""}
                onChange={(e) => update("max_value_eur", e.target.value)}
              />
            </Filter>
            <Filter label="Eligibility status">
              <select
                value={filters.eligibility_status ?? ""}
                onChange={(e) => update("eligibility_status", e.target.value)}
              >
                <option value="">All statuses</option>
                <option value="ELIGIBLE & CLEARED">Eligible</option>
                <option value="DOCUMENTATION REQUIRED">Needs documents</option>
                <option value="INELIGIBLE">Ineligible</option>
                <option value="NOT_ASSESSED">Not assessed</option>
              </select>
            </Filter>
          </div>
        )}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border px-5 py-3">
          <div className="flex items-center gap-3">
            <p className="text-xs font-medium" role="status" aria-live="polite">
              {result.loading
                ? "Finding players…"
                : result.error
                  ? "Players unavailable"
                  : `${players.length} ${players.length === 1 ? "player" : "players"}`}
            </p>
            {(filterCount > 0 || filters.q) && (
              <button
                onClick={reset}
                className="flex items-center gap-1 text-[11px] text-ink-muted hover:text-pitch"
              >
                <X size={12} />
                Clear all
              </button>
            )}
          </div>
          <label className="flex items-center gap-2 text-[11px] text-ink-muted">
            <ArrowDownUp size={12} />
            <span className="sr-only">Sort players</span>
            <select
              className="min-h-8! border-0! bg-transparent! py-1! text-[11px]!"
              value={filters.sort ?? "name"}
              onChange={(e) => update("sort", e.target.value)}
            >
              <option value="name">Name, A–Z</option>
              <option value="age_asc">Youngest first</option>
              <option value="value_desc">Highest value</option>
            </select>
          </label>
        </div>
        {result.loading ? (
          <div aria-label="Loading players" className="space-y-6 p-6">
            {Array.from({ length: 6 }, (_, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="skeleton h-10 w-10" />
                <div className="skeleton h-4 w-2/5" />
                <div className="skeleton ml-auto h-4 w-16" />
              </div>
            ))}
          </div>
        ) : result.error ? (
          <Empty
            title="The player database is unavailable"
            description="Check your connection and try again."
          >
            <button
              className="btn"
              onClick={() => {
                result.retry();
                inventory.retry();
              }}
            >
              Try again
            </button>
          </Empty>
        ) : players.length === 0 ? (
          <Empty
            title={
              shortlist && !visibleIds.length
                ? "A good eye starts a great shortlist"
                : "No players match your search"
            }
            description={
              shortlist && !visibleIds.length
                ? "Use the bookmark beside a player to save them here for your next scouting session."
                : "Try a different name or widen your filters."
            }
          >
            {shortlist && !visibleIds.length ? (
              <Link className="btn btn-primary" to={pathFor("/")}>
                Discover players
              </Link>
            ) : (
              <button className="btn" onClick={reset}>
                Reset filters
              </button>
            )}
          </Empty>
        ) : cards ? (
          <div className="grid grid-cols-1 gap-4 bg-shell/50 p-4 sm:grid-cols-2 xl:grid-cols-3">
            {shown.map((player) => (
              <PlayerCard key={player.id} player={player} />
            ))}
          </div>
        ) : (
          <>
            <div className="hidden overflow-x-auto md:block">
              <table className="player-table">
                <thead>
                  <tr>
                    <th>Player</th>
                    <th>Position</th>
                    <th>Age</th>
                    <th className="secondary-column">Est. value</th>
                    <th>Eligibility</th>
                    <th>
                      <span className="sr-only">Shortlist</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {shown.map((player) => (
                    <tr key={player.id}>
                      <td>
                        <div className="flex items-center gap-3">
                          <Avatar id={player.id} name={player.name ?? player.id} size={36} />
                          <div className="min-w-0">
                            <Link
                              className="player-name"
                              to={`/players/${encodeURIComponent(player.id)}`}
                              state={{ from: location.pathname + location.search }}
                            >
                              {player.name ?? player.id}
                            </Link>
                            <p
                              className="mt-1 max-w-64 truncate text-[10px] text-ink-muted"
                              title={player.league_band ?? ""}
                            >
                              {player.league_band ?? "League not recorded"}
                            </p>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="rounded border border-border bg-shell px-2 py-1 text-[10px]">
                          {player.position ?? "—"}
                        </span>
                      </td>
                      <td className="tabular-nums text-ink-muted">{player.age ?? "—"}</td>
                      <td className="secondary-column tabular-nums">
                        {formatValue(player.estimated_value_eur)}
                      </td>
                      <td>
                        <EligibilityPill status={player.ancestry_eligibility} />
                      </td>
                      <td>
                        <SaveButton id={player.id} name={player.name ?? player.id} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="grid gap-3 bg-shell/50 p-4 md:hidden">
              {shown.map((player) => (
                <PlayerCard key={player.id} player={player} />
              ))}
            </div>
          </>
        )}
        {players.length > 0 && !result.loading && !result.error && (
          <div className="flex items-center justify-between gap-3 border-t border-border px-5 py-4">
            <p className="text-[10px] text-ink-muted">
              Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, players.length)} of{" "}
              {players.length}
            </p>
            <div className="flex items-center gap-2">
              <button
                aria-label="Previous page"
                className="icon-button border border-border"
                disabled={page <= 1}
                onClick={() => update("page", String(page - 1))}
              >
                <ChevronLeft size={15} />
              </button>
              <span className="px-1 text-[11px] text-ink-muted">
                {page} / {totalPages}
              </span>
              <button
                aria-label="Next page"
                className="icon-button border border-border"
                disabled={page >= totalPages}
                onClick={() => update("page", String(page + 1))}
              >
                <ChevronRight size={15} />
              </button>
            </div>
          </div>
        )}
      </section>
      <div className="mt-5 flex flex-wrap items-center justify-between gap-2 text-[10px] leading-relaxed text-ink-muted">
        <span>
          {dataset === "synthetic"
            ? "Synthetic demo: all players, clubs, valuations and performance figures are fictional."
            : "Profiles reflect recorded data. Missing values mean unrecorded, not zero."}
        </span>
        <Link to={pathFor("/guide")} className="underline underline-offset-2 hover:text-pitch">
          Data sources & coverage
        </Link>
      </div>
    </div>
  );
}
function HeroStat({ label, value }: { label: string; value: number | undefined }) {
  return (
    <div className="border-r border-white/15 pr-10 last:border-r-0 last:pr-0">
      <p className="text-[10px] text-on-pitch-muted">{label}</p>
      <p className="mt-1.5 font-display text-[30px] font-medium leading-none tracking-tight text-on-pitch">
        {value ?? "—"}
        <span className="ml-2 text-[10px] font-normal tracking-normal text-on-pitch-muted">
          players
        </span>
      </p>
    </div>
  );
}
function Filter({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-2 text-[11px] text-ink-muted">
      {label}
      {children}
    </label>
  );
}
function Empty({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center px-6 py-20 text-center">
      <span className="mb-4 rounded-full bg-pitch-tint p-4 text-pitch">
        <Bookmark size={23} strokeWidth={1.5} />
      </span>
      <h2 className="font-display text-lg font-medium">{title}</h2>
      <p className="mb-5 mt-2 max-w-sm text-xs leading-relaxed text-ink-muted">{description}</p>
      {children}
    </div>
  );
}
