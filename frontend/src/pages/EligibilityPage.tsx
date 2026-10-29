import { useState } from "react";
import { useDataset } from "../lib/dataset-context";
import { Check, ClipboardCheck, FileCheck2, Loader2, RotateCcw, ShieldCheck } from "lucide-react";
import { evaluateEligibility } from "../api/client";
import type { EligibilityFacts, EligibilityResponse } from "../api/types";
const DEFAULTS: EligibilityFacts = {
  nationality_path: "DUAL_NATIONAL",
  born_in_territory: false,
  born_in_territory_documented: false,
  parent_born_in_territory: false,
  parent_born_in_territory_documented: false,
  grandparent_born_in_territory: false,
  grandparent_born_in_territory_documented: false,
  residency_years: 0,
  residency_years_after_18: 0,
  residency_documented: false,
  has_senior_caps_other_association: false,
  has_youth_caps_other_association: false,
  article8_switch_approved: false,
};
export function EligibilityPage() {
  const { dataset } = useDataset();
  const [facts, setFacts] = useState<EligibilityFacts>(DEFAULTS);
  const [result, setResult] = useState<EligibilityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  function set<K extends keyof EligibilityFacts>(key: K, value: EligibilityFacts[K]) {
    setFacts((f) => ({ ...f, [key]: value }));
    setResult(null);
    setError(null);
  }
  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setResult(null);
    setError(null);
    if (facts.residency_years_after_18 > facts.residency_years) {
      setError("Years after age 18 cannot exceed total residency. Check both residency fields.");
      return;
    }
    setSubmitting(true);
    try {
      setResult(await evaluateEligibility("screening", facts));
    } catch {
      setError("The assessment service is unavailable. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }
  return (
    <div>
      <h1 className="page-title">
        Eligibility checker<span className="text-pitch">.</span>
      </h1>
      <p className="page-description max-w-2xl">
        Turn known player facts into a preliminary screening. Keep supporting documents close for
        the association’s review.
      </p>
      {dataset === "synthetic" && (
        <section className="panel mt-6 p-4">
          <p className="mb-3 text-xs font-medium">Try a fictional scenario</p>
          <div className="flex flex-wrap gap-2">
            {[
              {
                label: "Documented parent",
                facts: {
                  parent_born_in_territory: true,
                  parent_born_in_territory_documented: true,
                },
              },
              { label: "Missing evidence", facts: { parent_born_in_territory: true } },
              {
                label: "Association switch",
                facts: {
                  parent_born_in_territory: true,
                  parent_born_in_territory_documented: true,
                  has_youth_caps_other_association: true,
                },
              },
            ].map((example) => (
              <button
                key={example.label}
                type="button"
                disabled={submitting}
                className="btn"
                onClick={() => {
                  setFacts({ ...DEFAULTS, ...example.facts });
                  setResult(null);
                  setError(null);
                }}
              >
                {example.label}
              </button>
            ))}
          </div>
          <p className="mt-3 text-[11px] text-ink-muted">
            Examples fill the form. Select Run preliminary check to see the result.
          </p>
        </section>
      )}
      <div className="mt-7 grid items-start gap-6 xl:grid-cols-[minmax(0,1fr)_320px]">
        <form onSubmit={submit} className="panel p-5 sm:p-7">
          <fieldset disabled={submitting} className="min-w-0 space-y-7">
            <section>
              <Heading
                number="01"
                title="Nationality pathway"
                description="Choose the player’s current nationality situation."
              />
              <label className="mt-4 flex flex-col gap-2 text-xs text-ink-muted">
                Pathway
                <select
                  value={facts.nationality_path}
                  onChange={(e) =>
                    set("nationality_path", e.target.value as EligibilityFacts["nationality_path"])
                  }
                >
                  <option value="DUAL_NATIONAL">Already holds Bangladeshi nationality</option>
                  <option value="NEW_NATIONALITY">Newly acquiring Bangladeshi nationality</option>
                </select>
              </label>
            </section>
            <section className="border-t border-border pt-6">
              <Heading
                number="02"
                title="Connection to Bangladesh"
                description="Select the known links, then mark the evidence you have verified."
              />
              <div className="mt-4 space-y-3">
                {(
                  [
                    ["born_in_territory", "Player born in Bangladesh"],
                    ["parent_born_in_territory", "Parent born in Bangladesh"],
                    ["grandparent_born_in_territory", "Grandparent born in Bangladesh"],
                  ] as const
                ).map(([key, label]) => {
                  const doc = `${key}_documented` as
                    | "born_in_territory_documented"
                    | "parent_born_in_territory_documented"
                    | "grandparent_born_in_territory_documented";
                  return (
                    <div
                      key={key}
                      className="flex flex-wrap items-center justify-between gap-3 rounded-control border border-border p-3.5"
                    >
                      <label className="flex items-center gap-2.5 text-xs">
                        <input
                          type="checkbox"
                          checked={facts[key]}
                          onChange={(e) => {
                            setFacts((f) => ({
                              ...f,
                              [key]: e.target.checked,
                              [doc]: e.target.checked ? f[doc] : false,
                            }));
                            setResult(null);
                            setError(null);
                          }}
                        />
                        {label}
                      </label>
                      <label
                        className={`flex items-center gap-2 text-[10px] ${facts[key] ? "text-pitch" : "text-ink-muted"}`}
                      >
                        <input
                          type="checkbox"
                          aria-label={`${label}: evidence verified`}
                          disabled={!facts[key]}
                          checked={facts[doc]}
                          onChange={(e) => set(doc, e.target.checked)}
                        />
                        Evidence verified
                      </label>
                    </div>
                  );
                })}
              </div>
            </section>
            <section className="border-t border-border pt-6">
              <Heading
                number="03"
                title="Residency"
                description="Enter continuous years of residence in Bangladesh."
              />
              <div className="mt-4 grid grid-cols-2 gap-4">
                <label className="flex flex-col gap-2 text-xs text-ink-muted">
                  Total years
                  <input
                    type="number"
                    required
                    min={0}
                    max={100}
                    step={1}
                    value={facts.residency_years}
                    onChange={(e) => set("residency_years", Number(e.target.value))}
                  />
                </label>
                <label className="flex flex-col gap-2 text-xs text-ink-muted">
                  Years after age 18
                  <input
                    type="number"
                    required
                    min={0}
                    max={facts.residency_years}
                    step={1}
                    value={facts.residency_years_after_18}
                    onChange={(e) => set("residency_years_after_18", Number(e.target.value))}
                  />
                </label>
              </div>
              <label className="mt-4 flex items-center gap-2.5 text-xs">
                <input
                  type="checkbox"
                  checked={facts.residency_documented}
                  onChange={(e) => set("residency_documented", e.target.checked)}
                />
                Residency evidence verified
              </label>
            </section>
            <section className="border-t border-border pt-6">
              <Heading
                number="04"
                title="Prior representation"
                description="Include official competition appearances for another association."
              />
              <div className="mt-4 space-y-3">
                <Checkbox
                  label="Senior appearances for another association"
                  checked={facts.has_senior_caps_other_association}
                  onChange={(v) => set("has_senior_caps_other_association", v)}
                />
                <Checkbox
                  label="Youth appearances for another association"
                  checked={facts.has_youth_caps_other_association}
                  onChange={(v) => set("has_youth_caps_other_association", v)}
                />
                <Checkbox
                  label="Change of association already approved"
                  checked={facts.article8_switch_approved}
                  onChange={(v) => set("article8_switch_approved", v)}
                />
              </div>
            </section>
            {error && (
              <p role="alert" className="rounded-panel bg-red-50 p-3 text-xs text-ineligible">
                {error}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-3 border-t border-border pt-5">
              <button type="submit" className="btn btn-primary">
                {submitting ? (
                  <Loader2 className="animate-spin" size={15} />
                ) : (
                  <ShieldCheck size={15} />
                )}
                {submitting ? "Assessing facts…" : "Run preliminary check"}
              </button>
              <button
                type="button"
                className="btn border-0!"
                onClick={() => {
                  setFacts(DEFAULTS);
                  setResult(null);
                  setError(null);
                }}
              >
                <RotateCcw size={13} />
                Reset
              </button>
            </div>
          </fieldset>
        </form>
        <aside className="space-y-5 xl:sticky xl:top-6">
          <section className="panel p-6" aria-live="polite" aria-atomic="true">
            {result ? (
              <>
                <span className="mb-4 inline-flex rounded-control bg-pitch-tint p-3 text-pitch">
                  <ClipboardCheck size={23} />
                </span>
                <h2 className="font-display text-xl font-semibold">
                  {result.status === "ELIGIBLE & CLEARED"
                    ? "Qualifying link recorded"
                    : result.status === "DOCUMENTATION REQUIRED"
                      ? "Further evidence needed"
                      : "No qualifying link found"}
                </h2>
                <p className="mt-2 text-xs leading-relaxed text-ink-muted">
                  {result.article8_switch_required
                    ? "Association-switch review is required before proceeding."
                    : "Submit verified facts to the relevant association for confirmation."}
                </p>
                <ul className="mt-5 space-y-3 border-t border-border pt-5">
                  {result.reasons.map((reason) => (
                    <li
                      key={reason}
                      className="flex gap-2 text-[11px] leading-relaxed text-ink-muted"
                    >
                      <Check size={13} className="mt-0.5 shrink-0 text-pitch" />
                      {reason}
                    </li>
                  ))}
                </ul>
              </>
            ) : (
              <>
                <span className="mb-4 inline-flex rounded-control bg-pitch-tint p-3 text-pitch">
                  <ShieldCheck size={23} strokeWidth={1.5} />
                </span>
                <h2 className="font-display text-lg font-medium">A clearer starting point.</h2>
                <p className="mt-3 text-xs leading-relaxed text-ink-muted">
                  Enter the player’s facts and run the check. The result will outline known links,
                  missing evidence and association-review needs.
                </p>
                <div className="mt-6 border-t border-border pt-5 text-[11px] text-ink-muted">
                  <p className="flex items-center gap-2">
                    <FileCheck2 size={14} />
                    Use verified documents
                  </p>
                  <p className="mt-3 flex items-center gap-2">
                    <Check size={14} />
                    Review every prior appearance
                  </p>
                </div>
              </>
            )}
          </section>
          <div className="rounded-panel border border-[var(--color-notice-border)] bg-[var(--color-notice)] p-5">
            <p className="text-xs font-medium text-[var(--color-notice-ink)]">
              Preliminary screening
            </p>
            <p className="mt-2 text-[11px] leading-relaxed text-[var(--color-notice-ink)]">
              This tool uses a simplified legacy ruleset. Nationality, residency exceptions and
              association switches require current FIFA and federation review.
            </p>
            <a
              href="https://inside.fifa.com/legal/news/updated-documentation-guidance-player-eligibility-change-association"
              target="_blank"
              rel="noreferrer"
              className="mt-3 inline-block text-[11px] font-medium text-pitch underline underline-offset-2"
            >
              Official FIFA guidance
            </a>
          </div>
        </aside>
      </div>
    </div>
  );
}
function Heading({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-control bg-pitch-tint font-display text-xs text-pitch">
        {number}
      </span>
      <div>
        <h2 className="font-display text-base font-medium">{title}</h2>
        <p className="mt-1 text-[11px] leading-relaxed text-ink-muted">{description}</p>
      </div>
    </div>
  );
}
function Checkbox({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2.5 text-xs">
      <input type="checkbox" checked={checked} onChange={(e) => onChange(e.target.checked)} />
      {label}
    </label>
  );
}
