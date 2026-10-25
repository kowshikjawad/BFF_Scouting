import type { EligibilityStatus } from "../api/types";

const STYLES: Record<EligibilityStatus, { color: string; bg: string; label: string }> = {
  "ELIGIBLE & CLEARED": { color: "#22c55e", bg: "#22c55e1f", label: "Eligible" },
  "DOCUMENTATION REQUIRED": { color: "#d4a24c", bg: "#d4a24c1f", label: "Docs required" },
  INELIGIBLE: { color: "#ef4444", bg: "#ef44441f", label: "Ineligible" },
};

export function EligibilityPill({ status }: { status: EligibilityStatus | null }) {
  if (!status) {
    return (
      <span className="rounded-[6px] border border-border px-2 py-0.5 text-xs text-ink-faint">
        Not assessed
      </span>
    );
  }
  const style = STYLES[status];
  return (
    <span
      className="rounded-[6px] px-2 py-0.5 text-xs font-medium"
      style={{ color: style.color, backgroundColor: style.bg }}
    >
      {style.label}
    </span>
  );
}
