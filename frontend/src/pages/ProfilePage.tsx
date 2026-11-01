import { useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { ArrowLeft, Download, FileCheck2, Info, Loader2, MapPin, ShieldCheck } from "lucide-react";
import {
  ApiError,
  downloadReport,
  getPlayer,
  getSimilarPlayers,
  searchPlayers,
} from "../api/client";
import {
  TACTICAL_METRICS,
  METRIC_LABELS,
  REFERENCE_METRICS,
  REFERENCE_METRIC_LABELS,
} from "../api/types";
import { Avatar } from "../components/Avatar";
import { EligibilityPill } from "../components/EligibilityPill";
import { SaveButton } from "../components/SaveButton";
import { TacticalRadar } from "../components/TacticalRadar";
import { SimilarityPanel, type SimilarityState } from "../components/SimilarityPanel";
import { formatMetric, formatReferenceMetric, formatValue } from "../lib/format";
import { useDataset } from "../lib/dataset-context";
import { useResource } from "../hooks/useResource";
export function ProfilePage() {
  const { id = "" } = useParams<{ id: string }>();
  return <ProfileContent key={id} id={id} />;
}
function ProfileContent({ id }: { id: string }) {
  const { dataset, pathFor } = useDataset();
  const resource = useResource(id, () => getPlayer(id));
  const pool = useResource(`profile-pool:${dataset}`, () => searchPlayers({ dataset }));
  const [similarity, setSimilarity] = useState<SimilarityState>({ status: "idle" });
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(false);
  const location = useLocation();
  const from =
    typeof location.state?.from === "string" &&
    /^\/(\?|shortlist(?:\?|$)|$)/.test(location.state.from)
      ? location.state.from
      : pathFor("/");
  async function findSimilar() {
    setSimilarity({ status: "loading" });
    try {
      const results = await getSimilarPlayers(id);
      setSimilarity(results.length ? { status: "ready", results } : { status: "empty" });
    } catch {
      setSimilarity({ status: "error" });
    }
  }
  async function exportPdf() {
    setExporting(true);
    setExportError(false);
    try {
      await downloadReport(id);
    } catch {
      setExportError(true);
    } finally {
      setExporting(false);
    }
  }
  if (resource.loading)
    return (
      <div className="panel space-y-6 p-8" aria-label="Loading player">
        <div className="skeleton h-20 w-20" />
        <div className="skeleton h-7 w-2/3" />
        <div className="skeleton h-52 w-full" />
      </div>
    );
  if (resource.error || !resource.data) {
    const missing = resource.error instanceof ApiError && resource.error.status === 404;
    return (
      <div className="panel px-6 py-24 text-center">
        <h1 className="page-title">{missing ? "Player not found" : "Couldn’t load this player"}</h1>
        <p className="page-description">
          {missing
            ? "This profile may have been removed from the database."
            : "The database is temporarily unavailable. Please try again."}
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Link to={from} className="btn">
            Back to discovery
          </Link>
          {!missing && (
            <button className="btn btn-primary" onClick={resource.retry}>
              Try again
            </button>
          )}
        </div>
      </div>
    );
  }
  const player = resource.data;
  const name = player.name ?? player.id;
  return (
    <div>
      <div className="mb-7 flex flex-wrap items-center justify-between gap-3">
        <Link to={from} className="flex items-center gap-2 text-xs text-ink-muted hover:text-pitch">
          <ArrowLeft size={14} />
          Back to {from.startsWith("/shortlist") ? "shortlist" : "discovery"}
        </Link>
        <div className="flex gap-2">
          <SaveButton id={id} name={name} full />
          <button className="btn btn-primary" onClick={exportPdf} disabled={exporting}>
            {exporting ? <Loader2 size={14} className="animate-spin" /> : <Download size={14} />}
            {exporting ? "Preparing…" : "Export report"}
          </button>
        </div>
      </div>
      {exportError && (
        <p
          role="alert"
          className="mb-5 rounded-panel bg-ineligible-tint p-3 text-xs text-ineligible"
        >
          The report could not be downloaded. Please try Export report again.
        </p>
      )}
      <section className="panel mb-6 p-6 sm:p-8">
        <div className="flex flex-wrap items-center gap-5">
          <Avatar id={id} name={name} size={72} />
          <div className="min-w-0 flex-1">
            <h1 className="page-title wrap-anywhere">{name}</h1>
            <p className="mt-2 flex items-start gap-1.5 text-xs leading-relaxed text-ink-muted">
              <MapPin size={14} className="shrink-0" />
              {player.league_band ?? "League not recorded"}
            </p>
          </div>
          <EligibilityPill status={player.ancestry_eligibility} />
        </div>
        <dl className="mt-7 grid grid-cols-2 gap-6 border-t border-border pt-6 sm:grid-cols-3 xl:grid-cols-6">
          <Fact label="Position" value={player.position ?? "Not recorded"} />
          <Fact label="Age" value={player.age != null ? `${player.age} years` : "Not recorded"} />
          <Fact label="Preferred foot" value={player.strong_foot ?? "Not recorded"} />
          <Fact
            label="Height"
            value={player.height_cm ? `${player.height_cm} cm` : "Not recorded"}
          />
          <Fact label="Estimated value" value={formatValue(player.estimated_value_eur)} />
          <Fact label="Contract expiry" value={player.contract_expiry ?? "Not recorded"} />
        </dl>
      </section>
      <div className="grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_300px]">
        <section className="panel p-6">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <h2 className="font-display text-lg font-semibold tracking-tight">
                Tactical profile
              </h2>
              <p className="mt-1 text-[11px] text-ink-muted">
                Performance in context, when coverage allows.
              </p>
            </div>
            <span className="rounded bg-shell px-2 py-1 text-[10px] text-ink-muted">
              Per 90 minutes
            </span>
          </div>
          <TacticalRadar player={player} pool={pool.data ?? []} />
          {Boolean(pool.error) && (
            <button className="mt-3 text-xs text-pitch underline" onClick={pool.retry}>
              Retry comparison data
            </button>
          )}
          <dl className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {TACTICAL_METRICS.map((metric) => (
              <div key={metric} className="rounded-control border border-border p-3">
                <dt className="text-[10px] text-ink-muted">{METRIC_LABELS[metric]}</dt>
                <dd className="mt-2 font-display text-xl font-medium tabular-nums">
                  {formatMetric(player[metric])}
                </dd>
              </div>
            ))}
          </dl>
          <div className="mt-6 border-t border-border pt-5">
            <p className="eyebrow mb-3">Additional stats</p>
            <dl className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {REFERENCE_METRICS.map((metric) => (
                <div key={metric} className="rounded-control bg-surface-raised p-3">
                  <dt className="text-[10px] text-ink-muted">{REFERENCE_METRIC_LABELS[metric]}</dt>
                  <dd className="mt-2 font-display text-base font-medium tabular-nums">
                    {formatReferenceMetric(metric, player[metric])}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </section>
        <div className="space-y-5">
          <section className="panel p-5">
            <div className="mb-4 flex items-center gap-2">
              <ShieldCheck size={17} className="text-pitch" />
              <h2 className="font-display text-base font-medium">Eligibility overview</h2>
            </div>
            <EligibilityPill status={player.ancestry_eligibility} />
            <p className="mt-3 text-xs leading-relaxed text-ink-muted">
              {player.ancestry_eligibility
                ? "This is a recorded screening status. In demo mode it is fictional; real clearance requires supporting documents and association confirmation."
                : "An eligibility assessment has not been recorded for this player. Use the checker when verified heritage and residency facts are available."}
            </p>
            <Link
              className="mt-4 inline-block text-xs font-medium text-pitch underline underline-offset-2"
              to={pathFor("/eligibility")}
            >
              Open eligibility checker
            </Link>
          </section>
          <section className="panel p-5">
            <h2 className="mb-1 font-display text-base font-medium">Similar players</h2>
            <p className="mb-4 text-[11px] leading-relaxed text-ink-muted">
              Find tactical alternatives from recorded metrics.
            </p>
            <SimilarityPanel state={similarity} onFind={findSimilar} />
          </section>
          <div className="flex gap-3 px-1 text-[11px] leading-relaxed text-ink-muted">
            <Info size={15} className="mt-0.5 shrink-0" />
            <p>
              Missing data is common outside covered leagues.{" "}
              <Link to={pathFor("/guide")} className="text-pitch underline underline-offset-2">
                Read about coverage
              </Link>
              .
            </p>
          </div>
        </div>
      </div>
      <div className="mt-6 flex items-center gap-2 text-[10px] text-ink-muted">
        <FileCheck2 size={13} />
        Export a one-page snapshot for your scouting notes.
      </div>
    </div>
  );
}
function Fact({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-[10px] text-ink-muted">{label}</dt>
      <dd className="mt-2 text-xs font-medium">{value}</dd>
    </div>
  );
}
