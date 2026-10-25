import { Link } from "react-router-dom";
import { ArrowRight, Loader2 } from "lucide-react";
import type { SimilarityResult } from "../api/types";

type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "empty" }
  | { status: "ready"; results: SimilarityResult[] }
  | { status: "error" };

export function SimilarityPanel({ state, onFind }: { state: State; onFind: () => void }) {
  if (state.status === "idle") {
    return (
      <button
        type="button"
        onClick={onFind}
        className="flex w-full items-center justify-center gap-2 rounded-[6px] border border-border-strong py-2.5 text-sm font-medium text-ink transition-colors hover:border-pitch hover:text-pitch"
      >
        Find similar players
        <ArrowRight size={15} />
      </button>
    );
  }

  if (state.status === "loading") {
    return (
      <div className="flex items-center justify-center gap-2 py-6 text-sm text-ink-muted">
        <Loader2 size={16} className="animate-spin" />
        Ranking similar players…
      </div>
    );
  }

  if (state.status === "error") {
    return (
      <p className="rounded-[6px] border border-ineligible/30 bg-ineligible/10 px-4 py-3 text-sm text-ineligible">
        Couldn't load similar players.
      </p>
    );
  }

  if (state.status === "empty") {
    return (
      <div className="rounded-[6px] border border-dashed border-border px-4 py-6 text-center">
        <p className="text-sm text-ink-muted">No similar players currently available.</p>
        <p className="mt-1 text-xs text-ink-faint">
          Similarity needs recorded tactical metrics on both sides — not yet the case for
          most players in this dataset.
        </p>
      </div>
    );
  }

  return (
    <ul className="flex flex-col gap-2">
      {state.results.map((result, i) => (
        <li key={result.player_id}>
          <Link
            to={`/players/${result.player_id}`}
            className="flex items-center justify-between rounded-[6px] border border-border bg-surface px-4 py-2.5 text-sm transition-colors hover:border-pitch/60"
          >
            <span className="flex items-center gap-3">
              <span className="font-display text-xs text-ink-faint">#{i + 1}</span>
              <span className="text-ink">{result.name ?? result.player_id}</span>
            </span>
            <span className="font-display font-semibold text-pitch">
              {result.similarity_score.toFixed(0)}%
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export type { State as SimilarityState };
