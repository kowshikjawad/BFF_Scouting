import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Download } from "lucide-react";
import { getPlayer, getSimilarPlayers, searchPlayers } from "../api/client";
import type { Player } from "../api/types";
import { TACTICAL_METRICS, METRIC_LABELS } from "../api/types";
import { Avatar } from "../components/Avatar";
import { EligibilityPill } from "../components/EligibilityPill";
import { TacticalRadar } from "../components/TacticalRadar";
import { SimilarityPanel, type SimilarityState } from "../components/SimilarityPanel";
import { formatMetric, formatValue } from "../lib/format";

export function ProfilePage() {
  const { id } = useParams<{ id: string }>();
  const [player, setPlayer] = useState<Player | null>(null);
  const [pool, setPool] = useState<Player[]>([]);
  const [notFound, setNotFound] = useState(false);
  const [similarity, setSimilarity] = useState<SimilarityState>({ status: "idle" });

  useEffect(() => {
    if (!id) return;
    setNotFound(false);
    setPlayer(null);
    setSimilarity({ status: "idle" });
    getPlayer(id)
      .then(setPlayer)
      .catch(() => setNotFound(true));
    searchPlayers({}).then(setPool).catch(() => setPool([]));
  }, [id]);

  function findSimilar() {
    if (!id) return;
    setSimilarity({ status: "loading" });
    getSimilarPlayers(id)
      .then((results) => setSimilarity(results.length ? { status: "ready", results } : { status: "empty" }))
      .catch(() => setSimilarity({ status: "error" }));
  }

  if (notFound) {
    return (
      <div className="flex flex-col items-center gap-4 py-24 text-center">
        <p className="text-sm text-ink-muted">No player found with that id.</p>
        <Link to="/" className="text-sm font-medium text-pitch hover:underline">
          Back to search
        </Link>
      </div>
    );
  }

  if (!player) {
    return <p className="py-16 text-center text-sm text-ink-muted">Loading player…</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <Link
          to="/"
          className="flex items-center gap-1.5 text-sm text-ink-muted hover:text-ink"
        >
          <ArrowLeft size={15} />
          Back to search
        </Link>
        <button
          type="button"
          onClick={() => window.print()}
          className="flex items-center gap-2 rounded-[6px] border border-border-strong px-3 py-1.5 text-sm font-medium text-ink transition-colors hover:border-pitch hover:text-pitch"
        >
          <Download size={14} />
          Export PDF
        </button>
      </div>

      <div id="print-root" className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <section className="flex flex-col gap-6 rounded-[6px] border border-border bg-surface p-6 lg:col-span-2">
          <div className="flex items-start gap-4">
            <Avatar id={player.id} name={player.name} size={64} />
            <div className="flex-1">
              <h1 className="font-display text-2xl font-semibold text-ink">{player.name}</h1>
              <p className="text-sm text-ink-muted">{player.league_band}</p>
              <div className="mt-2">
                <EligibilityPill status={player.ancestry_eligibility} />
              </div>
            </div>
          </div>

          <dl className="grid grid-cols-2 gap-4 border-y border-border py-4 sm:grid-cols-4">
            <Fact label="Age" value={player.age != null ? `${player.age}` : "—"} />
            <Fact label="Position" value={player.position} />
            <Fact label="Strong foot" value={player.strong_foot ?? "—"} />
            <Fact label="Height" value={player.height_cm ? `${player.height_cm} cm` : "—"} />
            <Fact label="Est. value" value={formatValue(player.estimated_value_eur)} />
            <Fact label="Contract" value={player.contract_expiry ?? "—"} />
          </dl>

          <div>
            <h2 className="mb-3 font-display text-sm font-semibold text-ink">
              Tactical profile
            </h2>
            <TacticalRadar player={player} pool={pool} />
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
            {TACTICAL_METRICS.map((metric) => (
              <div key={metric} className="rounded-[6px] border border-border px-3 py-2">
                <p className="text-[11px] text-ink-faint">{METRIC_LABELS[metric]}</p>
                <p className="font-display text-sm font-semibold text-ink">
                  {formatMetric(player[metric])}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="flex flex-col gap-3 print:hidden">
          <h2 className="font-display text-sm font-semibold text-ink">Similar players</h2>
          <SimilarityPanel state={similarity} onFind={findSimilar} />
        </section>
      </div>
    </div>
  );
}

function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[11px] text-ink-faint">{label}</dt>
      <dd className="font-display text-sm font-medium text-ink">{value}</dd>
    </div>
  );
}
