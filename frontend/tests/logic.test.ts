import { test } from "node:test";
import assert from "node:assert/strict";
import { parseShortlist } from "../src/lib/shortlist-storage.ts";
import { tacticalComparison } from "../src/lib/tactical.ts";
import type { Player } from "../src/api/types.ts";

test("corrupted or invalid shortlist storage is safely recovered", () => {
  assert.deepEqual(parseShortlist("{corrupt"), []);
  assert.deepEqual(parseShortlist('{"id":"p1"}'), []);
  assert.deepEqual(parseShortlist('["p1",null,7,"p1","p2",""]'), ["p1", "p2"]);
});
const player = (id: string, overrides = {}): Player => ({
  id,
  name: id,
  age: null,
  position: "DM",
  height_cm: null,
  strong_foot: null,
  league_band: "League -- Club",
  contract_expiry: null,
  estimated_value_eur: null,
  ancestry_eligibility: null,
  goals_per_90: 0.3,
  key_passes_per_90: 2,
  progressive_carries_per_90: 3,
  tackles_won_per_90: 1,
  aerial_duel_pct: 70,
  ...overrides,
});
test("tactical comparisons preserve missing-data semantics", () => {
  assert.equal(tacticalComparison(player("p", { goals_per_90: null }), [player("peer")]), null);
  assert.equal(tacticalComparison(player("p"), [player("peer", { league_band: "Other" })]), null);
});
test("tactical comparison uses same-league role peers and comparable percentile axes", () => {
  const comparison = tacticalComparison(player("p"), [
    player("peer", {
      position: "Defensive Midfielder",
      league_band: "League -- Other club",
      aerial_duel_pct: 40,
    }),
    player("wrong", { position: "GK" }),
  ]);
  assert.equal(comparison?.count, 2);
  assert.equal(comparison?.data.find((row) => row.metric === "aerial_duel_pct")?.player, 75);
  assert.ok(comparison?.data.every((row) => row.player >= 0 && row.player <= 100));
});

test("a matching league label cannot mix synthetic and real radar cohorts", () => {
  assert.equal(tacticalComparison(player("synthetic-v1-demo"), [player("real-peer")]), null);
});
