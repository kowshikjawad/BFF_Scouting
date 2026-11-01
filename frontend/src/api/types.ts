// Mirrors backend/models/player.py::Player and backend/eligibility/engine.py.

export type EligibilityStatus = "ELIGIBLE & CLEARED" | "DOCUMENTATION REQUIRED" | "INELIGIBLE";

export interface Player {
  data_source?: "real" | "synthetic";
  id: string;
  name: string | null;
  age: number | null;
  position: string | null;
  height_cm: number | null;
  strong_foot: "Left" | "Right" | "Both" | null;
  league_band: string | null;
  contract_expiry: string | null;
  estimated_value_eur: number | null;
  ancestry_eligibility: EligibilityStatus | null;
  goals_per_90?: number | null;
  assists_per_90?: number | null;
  key_passes_per_90?: number | null;
  progressive_carries_per_90?: number | null;
  dribbles_per_90?: number | null;
  tackles_won_per_90?: number | null;
  interceptions_per_90?: number | null;
  aerial_duel_pct?: number | null;
  shots_per_90?: number | null;
  shot_accuracy_pct?: number | null;
  pass_completion_pct?: number | null;
  clearances_per_90?: number | null;
  minutes_played?: number | null;
  appearances?: number | null;
}

// Radar/similarity comparison vector (mirrors ml/features/normalize.py).
export const TACTICAL_METRICS = [
  "goals_per_90",
  "assists_per_90",
  "key_passes_per_90",
  "progressive_carries_per_90",
  "dribbles_per_90",
  "tackles_won_per_90",
  "interceptions_per_90",
  "aerial_duel_pct",
] as const;

export type TacticalMetric = (typeof TACTICAL_METRICS)[number];

export const METRIC_LABELS: Record<TacticalMetric, string> = {
  goals_per_90: "Goals /90",
  assists_per_90: "Assists /90",
  key_passes_per_90: "Key Passes /90",
  progressive_carries_per_90: "Prog. Carries /90",
  dribbles_per_90: "Dribbles /90",
  tackles_won_per_90: "Tackles Won /90",
  interceptions_per_90: "Interceptions /90",
  aerial_duel_pct: "Aerial Duel %",
};

// Recorded stats shown on a profile but not part of the radar/similarity
// vector (season totals, or there simply isn't room for a 9th+ radar axis).
export const REFERENCE_METRICS = [
  "shots_per_90",
  "shot_accuracy_pct",
  "pass_completion_pct",
  "clearances_per_90",
  "minutes_played",
  "appearances",
] as const;

export type ReferenceMetric = (typeof REFERENCE_METRICS)[number];

export const REFERENCE_METRIC_LABELS: Record<ReferenceMetric, string> = {
  shots_per_90: "Shots /90",
  shot_accuracy_pct: "Shot Accuracy %",
  pass_completion_pct: "Pass Completion %",
  clearances_per_90: "Clearances /90",
  minutes_played: "Minutes Played",
  appearances: "Appearances",
};

export interface SearchFilters {
  dataset?: "real" | "synthetic";
  q?: string;
  sort?: "name" | "age_asc" | "value_desc";
  eligibility_status?: EligibilityStatus | "NOT_ASSESSED";
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
  reasons: string[];
  review_required: boolean;
  ruleset: string;
}
