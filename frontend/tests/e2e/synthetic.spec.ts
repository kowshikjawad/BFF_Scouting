import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";

test("the default demo provides complete real API charts, similarity, shortlist and PDF export", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.getByLabel("Data source")).toHaveValue("synthetic");
  await expect(page.getByRole("note")).toContainText("Fictional players");
  await expect(page.getByRole("status")).toContainText("160 players");
  await page.getByRole("table").getByRole("link").first().click();
  await expect(page.getByRole("img", { name: /Tactical percentile comparison/ })).toBeVisible();
  const name = await page.getByRole("heading", { level: 1 }).innerText();
  await expect(
    page.getByText("Percentile scale · 4 players · same league & position"),
  ).toBeVisible();
  await page.getByRole("button", { name: "Find similar players" }).click();
  await expect(page.locator("main ul li")).toHaveCount(5);
  await expect(page.locator("main ul li").first()).toContainText("%");
  const matches = await page
    .locator("main ul a")
    .evaluateAll((nodes) => nodes.map((node) => node.getAttribute("href")));
  expect(matches.every((path) => path?.includes("synthetic-v1-"))).toBe(true);
  await page.getByRole("button", { name: `Save ${name} to shortlist` }).click();
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export report" }).click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toContain("synthetic-v1-");
  expect((await readFile((await download.path())!)).subarray(0, 4).toString()).toBe("%PDF");
  await page.getByRole("link", { name: "My shortlist" }).click();
  await expect(page.getByRole("link", { name, exact: true })).toBeVisible();
  await page.getByLabel("Data source").selectOption("real");
  await expect(page.getByRole("note")).toHaveCount(0);
  await page.getByRole("link", { name: "My shortlist" }).click();
  await expect(
    page.getByRole("heading", { name: "A good eye starts a great shortlist" }),
  ).toBeVisible();
  await page.getByLabel("Data source").selectOption("synthetic");
  await page.getByRole("link", { name: "My shortlist" }).click();
  await page.reload();
  await expect(page.getByRole("link", { name, exact: true })).toBeVisible();
});

test("fictional eligibility scenarios exercise all three example flows", async ({ page }) => {
  await page.goto("/eligibility?dataset=synthetic");
  for (const [example, heading] of [
    ["Documented parent", "Qualifying link recorded"],
    ["Missing evidence", "Further evidence needed"],
    ["Association switch", "Further evidence needed"],
  ]) {
    await page.getByRole("button", { name: example, exact: true }).click();
    await page.getByRole("button", { name: "Run preliminary check" }).click();
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  }
});

test("demo explanation and complete profile fit mobile", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await page.goto("/guide?dataset=synthetic");
  await expect(page.getByRole("heading", { name: "How the synthetic demo works" })).toBeVisible();
  await page.getByRole("link", { name: "Open a complete demo profile" }).click();
  await expect(page.getByRole("heading", { name: "Arian Rahman" })).toBeVisible();
  await expect(page.getByRole("img", { name: /Tactical percentile comparison/ })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  );
});
