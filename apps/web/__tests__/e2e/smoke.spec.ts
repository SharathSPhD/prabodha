import { test, expect } from "@playwright/test";

test.describe("smoke tests", () => {
  test("landing page renders", async ({ page }) => {
    await page.goto("/");
    await expect(page.locator("h1")).toContainText("Recognition");
    await expect(page.locator("a[href='/theatre']")).toBeVisible();
  });

  test("login page renders", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("input[type='email']")).toBeVisible();
  });

  test("glossary page loads", async ({ page }) => {
    await page.goto("/glossary");
    await expect(page.locator("h1")).toContainText("Glossary");
    await expect(page.locator("text=vimarśa")).toBeVisible();
  });

  test("results page loads", async ({ page }) => {
    await page.goto("/results");
    await expect(page.locator("h1")).toContainText("Results");
  });

  test("theatre page renders tabs", async ({ page }) => {
    await page.goto("/theatre");
    await expect(page.locator("button:has-text('Replay')")).toBeVisible();
    await expect(page.locator("button:has-text('Live (admin)')")).toBeVisible();
    await expect(page.locator("button:has-text('BYOK')")).toBeVisible();
  });

  test("unauthenticated /dashboard redirect", async ({ page }) => {
    await page.goto("/dashboard");
    // Should redirect to /login
    await expect(page).toHaveURL(/\/login/);
  });
});
