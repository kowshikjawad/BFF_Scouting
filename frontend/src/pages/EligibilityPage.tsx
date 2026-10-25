import { useState } from "react";
import { evaluateEligibility } from "../api/client";
import type { EligibilityFacts, EligibilityResponse } from "../api/types";
import { EligibilityPill } from "../components/EligibilityPill";

const DEFAULT_FACTS: EligibilityFacts = {
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
  const [facts, setFacts] = useState<EligibilityFacts>(DEFAULT_FACTS);
  const [result, setResult] = useState<EligibilityResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function set<K extends keyof EligibilityFacts>(key: K, value: EligibilityFacts[K]) {
    setFacts((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const res = await evaluateEligibility("checker", facts);
      setResult(res);
    } catch {
      setError("Couldn't evaluate eligibility.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink">
          FIFA eligibility checker
        </h1>
        <p className="mt-1 text-sm text-ink-muted">
          Evaluate a player's international eligibility under FIFA Statutes Art. 6
          (dual national), Art. 7 (new nationality), and Art. 8 (association switch).
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5 rounded-[6px] border border-border bg-surface p-6">
        <Field label="Nationality path">
          <select
            value={facts.nationality_path}
            onChange={(e) => set("nationality_path", e.target.value as EligibilityFacts["nationality_path"])}
          >
            <option value="DUAL_NATIONAL">Dual national (Art. 6 — 2yr residency)</option>
            <option value="NEW_NATIONALITY">New nationality (Art. 7 — 5yr post-18)</option>
          </select>
        </Field>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-xs font-medium text-ink-muted">Genuine link facts</legend>
          <CheckboxWithDoc
            label="Born in territory"
            checked={facts.born_in_territory}
            onCheck={(v) => set("born_in_territory", v)}
            documented={facts.born_in_territory_documented}
            onDocument={(v) => set("born_in_territory_documented", v)}
          />
          <CheckboxWithDoc
            label="Parent born in territory"
            checked={facts.parent_born_in_territory}
            onCheck={(v) => set("parent_born_in_territory", v)}
            documented={facts.parent_born_in_territory_documented}
            onDocument={(v) => set("parent_born_in_territory_documented", v)}
          />
          <CheckboxWithDoc
            label="Grandparent born in territory"
            checked={facts.grandparent_born_in_territory}
            onCheck={(v) => set("grandparent_born_in_territory", v)}
            documented={facts.grandparent_born_in_territory_documented}
            onDocument={(v) => set("grandparent_born_in_territory_documented", v)}
          />
        </fieldset>

        <fieldset className="flex flex-wrap items-end gap-4">
          <legend className="mb-1 w-full text-xs font-medium text-ink-muted">Residency</legend>
          <Field label="Residency (years)">
            <input
              type="number"
              min={0}
              value={facts.residency_years}
              onChange={(e) => set("residency_years", Number(e.target.value))}
              className="w-24"
            />
          </Field>
          <Field label="Residency after age 18 (years)">
            <input
              type="number"
              min={0}
              value={facts.residency_years_after_18}
              onChange={(e) => set("residency_years_after_18", Number(e.target.value))}
              className="w-24"
            />
          </Field>
          <label className="flex items-center gap-2 pb-1.5 text-sm text-ink-muted">
            <input
              type="checkbox"
              checked={facts.residency_documented}
              onChange={(e) => set("residency_documented", e.target.checked)}
              className="h-4 w-4 accent-pitch"
            />
            Documented
          </label>
        </fieldset>

        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-xs font-medium text-ink-muted">
            Article 8 — prior representation
          </legend>
          <label className="flex items-center gap-2 text-sm text-ink-muted">
            <input
              type="checkbox"
              checked={facts.has_senior_caps_other_association}
              onChange={(e) => set("has_senior_caps_other_association", e.target.checked)}
              className="h-4 w-4 accent-pitch"
            />
            Has senior caps for another association
          </label>
          <label className="flex items-center gap-2 text-sm text-ink-muted">
            <input
              type="checkbox"
              checked={facts.has_youth_caps_other_association}
              onChange={(e) => set("has_youth_caps_other_association", e.target.checked)}
              className="h-4 w-4 accent-pitch"
            />
            Has youth caps for another association
          </label>
          <label className="flex items-center gap-2 text-sm text-ink-muted">
            <input
              type="checkbox"
              checked={facts.article8_switch_approved}
              onChange={(e) => set("article8_switch_approved", e.target.checked)}
              className="h-4 w-4 accent-pitch"
            />
            Article 8 switch already approved
          </label>
        </fieldset>

        <button
          type="submit"
          disabled={submitting}
          className="rounded-[6px] bg-pitch px-4 py-2.5 text-sm font-semibold text-shell transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {submitting ? "Evaluating…" : "Evaluate eligibility"}
        </button>
      </form>

      {error && (
        <p className="rounded-[6px] border border-ineligible/30 bg-ineligible/10 px-4 py-3 text-sm text-ineligible">
          {error}
        </p>
      )}

      {result && (
        <div className="flex items-center justify-between rounded-[6px] border border-border bg-surface p-5">
          <div>
            <p className="text-xs text-ink-faint">Result</p>
            <p className="font-display text-lg font-semibold text-ink">{result.status}</p>
            {result.article8_switch_required && (
              <p className="mt-1 text-xs text-ink-muted">
                Article 8 switch {result.article8_switch_approved ? "approved" : "required, not yet approved"}
              </p>
            )}
          </div>
          <EligibilityPill status={result.status} />
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5 text-xs font-medium text-ink-muted">
      {label}
      {children}
    </label>
  );
}

function CheckboxWithDoc({
  label,
  checked,
  onCheck,
  documented,
  onDocument,
}: {
  label: string;
  checked: boolean;
  onCheck: (v: boolean) => void;
  documented: boolean;
  onDocument: (v: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-[6px] border border-border px-3 py-2">
      <label className="flex items-center gap-2 text-sm text-ink">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onCheck(e.target.checked)}
          className="h-4 w-4 accent-pitch"
        />
        {label}
      </label>
      <label className="flex items-center gap-1.5 text-xs text-ink-faint">
        <input
          type="checkbox"
          checked={documented}
          onChange={(e) => onDocument(e.target.checked)}
          disabled={!checked}
          className="h-3.5 w-3.5 accent-gold"
        />
        Documented
      </label>
    </div>
  );
}
