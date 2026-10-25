// Mirrors backend/models/player.py::Player and backend/eligibility/engine.py.

export type EligibilityStatus =
  | "ELIGIBLE & CLEARED"
  | "DOCUMENTATION REQUIRED"
  | "INELIGIBLE";

export interface Player {
  id: string;
  name: string;
  age: number | null;
  position: string;
  height_cm: number | null;
  strong_foot: "Left" | "Right" | "Both" | null;
  league_band: string;
  contract_expiry: string | null;
  estimated_value_eur: number | null;
  ancestry_eligibility: EligibilityStatus | null;
  goals_per_90?: number | null;
  key_passes_per_90?: number | null;
  progressive_carries_per_90?: number | null;
  tackles_won_per_90?: number | null;
  aerial_duel_pct?: number | null;
}

export const TACTICAL_METRICS = [
  "goals_per_90",
  "key_passes_per_90",
  "progressive_carries_per_90",
  "tackles_won_per_90",
  "aerial_duel_pct",
] as const;

export type TacticalMetric = (typeof TACTICAL_METRICS)[number];

export const METRIC_LABELS: Record<TacticalMetric, string> = {
  goals_per_90: "Goals /90",
  key_passes_per_90: "Key Passes /90",
  progressive_carries_per_90: "Prog. Carries /90",
  tackles_won_per_90: "Tackles Won /90",
  aerial_duel_pct: "Aerial Duel %",
};

export interface SearchFilters {
  max_age?: number;
  position?: string;
  strong_foot?: "Left" | "Right" | "Both";
  max_value_eur?: number;
  diaspora_eligible?: boolean;
}

export interface SimilarityResult {
  player_id: string;
  name: string | null;
  similarity_score: number;
}

export interface EligibilityFacts {
  nationality_path: "DUAL_NATIONAL" | "NEW_NATIONALITY";
  born_in_territory: boolean;
  born_in_territory_documented: boolean;
  parent_born_in_territory: boolean;
  parent_born_in_territory_documented: boolean;
  grandparent_born_in_territory: boolean;
  grandparent_born_in_territory_documented: boolean;
  residency_years: number;
  residency_years_after_18: number;
  residency_documented: boolean;
  has_senior_caps_other_association: boolean;
  has_youth_caps_other_association: boolean;
  article8_switch_approved: boolean;
}

export interface EligibilityResponse {
  player_id: string;
  status: EligibilityStatus;
  article8_switch_required: boolean;
  article8_switch_approved: boolean;
}
