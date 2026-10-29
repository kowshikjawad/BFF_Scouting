import type { EligibilityStatus } from "../api/types";
const STYLES: Record<EligibilityStatus, { style: string; label: string }> = {
  "ELIGIBLE & CLEARED": { style: "text-pitch bg-pitch-tint", label: "Eligible" },
  "DOCUMENTATION REQUIRED": { style: "text-gold bg-gold-tint", label: "Needs documents" },
  INELIGIBLE: { style: "text-ineligible bg-red-50", label: "Ineligible" },
};
export function EligibilityPill({ status }: { status: EligibilityStatus | null }) {
  const item = status
    ? STYLES[status]
    : { style: "text-ink-muted bg-surface-raised", label: "Not assessed" };
  return (
    <span
      title={status ?? "No recorded eligibility assessment"}
      className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded px-2 py-1 text-[10px] font-medium ${item.style}`}
    >
      <span className="h-1 w-1 rounded-full bg-current" />
      {item.label}
    </span>
  );
}
