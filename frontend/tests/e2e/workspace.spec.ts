import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("shonartalent.dataset.v1", "real"));
});

test("search, inspect, save, reload and download a report", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("searchbox", { name: "Search players by name" }).fill("Hamza");
  await expect(page.getByRole("link", { name: "Hamza Choudhury", exact: true })).toBeVisible();
  await page.getByRole("link", { name: "Hamza Choudhury", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Hamza Choudhury" })).toBeVisible();
  await expect(page.getByText("Tactical data is still taking shape")).toBeVisible();
  await page.getByRole("button", { name: "Save Hamza Choudhury to shortlist" }).click();
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export report" }).click();
  expect((await download).suggestedFilename()).toBe("hamza-choudhury-scout-report.pdf");
  await page.getByRole("link", { name: "Back to discovery" }).click();
  await expect(page.getByRole("searchbox")).toHaveValue("Hamza");
  await page.getByRole("link", { name: "My shortlist" }).click();
  await page.reload();
  await expect(page.getByRole("link", { name: "Hamza Choudhury", exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Remove Hamza Choudhury from shortlist" }).click();
  await expect(
    page.getByRole("heading", { name: "A good eye starts a great shortlist" }),
  ).toBeVisible();
});

test("URL filters, sort, card view and empty-state recovery", async ({ page }) => {
  await page.goto("/?position=DM&sort=age_asc&view=cards");
  await page.getByRole("button", { name: "Filters" }).click();
  await expect(page.getByRole("combobox", { name: "Position", exact: true })).toHaveValue("DM");
  await expect(page.getByLabel("Sort players")).toHaveValue("age_asc");
  await expect(page.getByRole("button", { name: "Card view" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await page.getByRole("searchbox").fill("unfindable-name");
  await expect(page.getByRole("heading", { name: "No players match your search" })).toBeVisible();
  await page.getByRole("button", { name: "Reset filters" }).click();
  await expect(page.locator("article").first()).toBeVisible();
  await expect(page.getByRole("searchbox")).toHaveValue("");
});

test("eligibility explains results and clears stale assessments", async ({ page }) => {
  await page.goto("/eligibility");
  await page.getByLabel("Player born in Bangladesh", { exact: true }).check();
  await page.getByLabel("Player born in Bangladesh: evidence verified", { exact: true }).check();
  await page.getByRole("button", { name: "Run preliminary check" }).click();
  await expect(page.getByRole("heading", { name: "Qualifying link recorded" })).toBeVisible();
  await page.getByLabel("Youth appearances for another association").check();
  await expect(page.getByRole("heading", { name: "Qualifying link recorded" })).toHaveCount(0);
  await page.getByRole("button", { name: "Run preliminary check" }).click();
  await expect(page.getByRole("heading", { name: "Further evidence needed" })).toBeVisible();
});

test("failed directory request can be retried", async ({ page }) => {
  let unavailable = true;
  await page.route(/\/api\/v1\/players(?:\?.*)?$/, (route) =>
    unavailable ? route.fulfill({ status: 503, body: "unavailable" }) : route.continue(),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "The player database is unavailable" }),
  ).toBeVisible();
  unavailable = false;
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByRole("table").getByRole("row").nth(1)).toBeVisible();
});

test("unknown player is distinct from a network error", async ({ page }) => {
  await page.goto("/players/unknown-profile");
  await expect(page.getByRole("heading", { name: "Player not found" })).toBeVisible();
});

test("mobile navigation and core screens fit 360 pixels", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  for (const path of ["/", "/players/hamza-choudhury", "/eligibility", "/guide"]) {
    await page.goto(path);
    await expect(page.locator("h1")).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true);
  }
  await page.getByRole("button", { name: "Open navigation" }).click();
  await expect(page.getByRole("link", { name: "My shortlist" })).toBeVisible();
  await page.getByRole("link", { name: "My shortlist" }).click();
  await expect(page.getByRole("heading", { name: "My shortlist" })).toBeVisible();
});

test("pagination and invalid storage recover without losing directory state", async ({ page }) => {
  const players = Array.from({ length: 25 }, (_, i) => ({
    id: `fixture-${i}`,
    name: `Test Prospect ${i}`,
    position: "CM",
    age: 20,
    league_band: "Test league",
    height_cm: null,
    strong_foot: null,
    contract_expiry: null,
    estimated_value_eur: null,
    ancestry_eligibility: null,
  }));
  await page.addInitScript(() => localStorage.setItem("shonartalent.shortlist.v1", "{broken"));
  await page.route(/\/api\/v1\/players(?:\?.*)?$/, (route) => route.fulfill({ json: players }));
  await page.goto("/");
  await expect(page.getByText("Showing 1–12 of 25")).toBeVisible();
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.getByText("Showing 13–24 of 25")).toBeVisible();
  await expect(page).toHaveURL(/page=2/);
  await page.reload();
  await expect(page.getByText("Showing 13–24 of 25")).toBeVisible();
});

test("a complete recorded cohort renders a normalized radar", async ({ page }) => {
  const reference = {
    id: "chart-reference",
    name: "Chart Test Player",
    position: "DM",
    age: 23,
    league_band: "Test League -- Reference Club",
    height_cm: null,
    strong_foot: "Right",
    contract_expiry: null,
    estimated_value_eur: null,
    ancestry_eligibility: null,
    goals_per_90: 0.3,
    key_passes_per_90: 2,
    progressive_carries_per_90: 3,
    tackles_won_per_90: 1,
    aerial_duel_pct: 70,
  };
  const peer = {
    ...reference,
    id: "chart-peer",
    name: "Chart Test Peer",
    league_band: "Test League -- Peer Club",
    aerial_duel_pct: 40,
  };
  await page.route(/\/api\/v1\/players(?:\?.*)?$/, (route) =>
    route.fulfill({ json: [reference, peer] }),
  );
  await page.route("**/api/v1/players/chart-reference", (route) =>
    route.fulfill({ json: reference }),
  );
  await page.goto("/players/chart-reference");
  await expect(page.getByRole("img", { name: /Tactical percentile comparison/ })).toBeVisible();
  await expect(
    page.getByText("Percentile scale · 2 players · same league & position"),
  ).toBeVisible();
});

test("blocked storage keeps a working session shortlist with a notice", async ({ page }) => {
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => {
      throw new Error("Storage blocked");
    };
  });
  await page.goto("/players/hamza-choudhury");
  await page.getByRole("button", { name: "Save Hamza Choudhury to shortlist" }).click();
  await expect(
    page.getByText(
      "Browser storage is unavailable. Your shortlist will last for this session only.",
    ),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Remove Hamza Choudhury from shortlist" }),
  ).toBeVisible();
});
