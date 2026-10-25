import { X } from "lucide-react";
import type { SearchFilters } from "../api/types";

const POSITIONS = [
  "GK", "CB", "LB", "RB", "DM", "CM", "AM", "LW", "RW", "ST",
];

interface Props {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
}

export function FilterBar({ filters, onChange }: Props) {
  const hasFilters = Object.keys(filters).length > 0;

  function set<K extends keyof SearchFilters>(key: K, value: SearchFilters[K] | undefined) {
    const next = { ...filters };
    if (value === undefined || value === "") {
      delete next[key];
    } else {
      next[key] = value;
    }
    onChange(next);
  }

  return (
    <div className="flex flex-wrap items-end gap-4 rounded-[6px] border border-border bg-surface p-4">
      <Field label="Max age">
        <input
          type="number"
          min={14}
          max={45}
          placeholder="Any"
          value={filters.max_age ?? ""}
          onChange={(e) => set("max_age", e.target.value ? Number(e.target.value) : undefined)}
          className="w-20"
        />
      </Field>

      <Field label="Position">
        <select
          value={filters.position ?? ""}
          onChange={(e) => set("position", e.target.value || undefined)}
        >
          <option value="">Any</option>
          {POSITIONS.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </Field>

      <Field label="Strong foot">
        <select
          value={filters.strong_foot ?? ""}
          onChange={(e) =>
            set("strong_foot", (e.target.value || undefined) as SearchFilters["strong_foot"])
          }
        >
          <option value="">Any</option>
          <option value="Left">Left</option>
          <option value="Right">Right</option>
          <option value="Both">Both</option>
        </select>
      </Field>

      <Field label="Max value (€)">
        <input
          type="number"
          min={0}
          step={50000}
          placeholder="Any"
          value={filters.max_value_eur ?? ""}
          onChange={(e) =>
            set("max_value_eur", e.target.value ? Number(e.target.value) : undefined)
          }
          className="w-28"
        />
      </Field>

      <label className="flex cursor-pointer items-center gap-2 pb-1.5 text-sm text-ink-muted">
        <input
          type="checkbox"
          checked={filters.diaspora_eligible === true}
          onChange={(e) => set("diaspora_eligible", e.target.checked ? true : undefined)}
          className="h-4 w-4 rounded-sm border-border-strong accent-pitch"
        />
        Diaspora eligible only
      </label>

      {hasFilters && (
        <button
          type="button"
          onClick={() => onChange({})}
          className="ml-auto flex items-center gap-1 rounded-[6px] px-2 py-1.5 text-sm text-ink-faint transition-colors hover:text-ink"
        >
          <X size={14} />
          Clear filters
        </button>
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
