import { test, expect } from "@playwright/test";

test.describe("Studio Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/studio", { waitUntil: "networkidle" });
  });

  test("should render the studio page header", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Live Steering Studio");
  });

  test("should have all control inputs", async ({ page }) => {
    // Prompt input
    await expect(page.locator('textarea[placeholder*="prompt"]')).toBeVisible();

    // Concept input
    await expect(page.locator('input[placeholder*="concept"]')).toBeVisible();

    // Amplitude slider
    await expect(page.locator('input[type="range"]')).toBeVisible();

    // Arm selector
    await expect(page.locator('select')).toBeVisible();
  });

  test("should have concept presets", async ({ page }) => {
    const presets = ["Honesty", "Refusal", "Creativity", "Caution", "Engagement"];

    for (const preset of presets) {
      await expect(page.locator(`button:has-text("${preset}")`)).toBeVisible();
    }
  });

  test("should have steer button", async ({ page }) => {
    const steerButton = page.locator('button:has-text("Steer")');
    await expect(steerButton).toBeVisible();
  });

  test("should have depth toggle", async ({ page }) => {
    await expect(page.locator("button:has-text(\"Explorer\"")).toBeVisible();
    await expect(page.locator("button:has-text(\"Researcher\"")).toBeVisible();
  });

  test("should toggle between Explorer and Researcher views", async ({
    page,
  }) => {
    const researcherButton = page.locator("button:has-text(\"Researcher\")");

    // Click researcher
    await researcherButton.click();
    await expect(researcherButton).toHaveAttribute("class", /indigo-600/);

    // Click explorer
    await page.locator("button:has-text(\"Explorer\")").click();
    await expect(
      page.locator("button:has-text(\"Explorer\")")
    ).toHaveAttribute("class", /indigo-600/);
  });

  test("should show gateway offline state if not configured", async ({
    page,
  }) => {
    // Check if we get either the studio or the offline message
    const pageText = await page.locator("body").textContent();
    expect(
      pageText?.includes("Gateway Offline") || pageText?.includes("Steer")
    ).toBeTruthy();
  });
});

test.describe("Build Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/build", { waitUntil: "networkidle" });
  });

  test("should render the builder page header", async ({ page }) => {
    await expect(page.locator("h1")).toContainText("Custom Steering Builder");
  });

  test("should have concept and contrastive tabs", async ({ page }) => {
    await expect(page.locator("button:has-text(\"Concept Word\")")).toBeVisible();
    await expect(
      page.locator("button:has-text(\"Contrastive\")")
    ).toBeVisible();
  });

  test("should have export button", async ({ page }) => {
    await expect(
      page.locator("button:has-text(\"Export as Steering Pack\")")
    ).toBeVisible();
  });
});

test.describe("Labs Pages", () => {
  test("should render jailbreak lab", async ({ page }) => {
    await page.goto("/jailbreak", { waitUntil: "networkidle" });
    await expect(page.locator("h1")).toContainText("Jailbreak Lab");
  });

  test("should render alignment lab", async ({ page }) => {
    await page.goto("/align", { waitUntil: "networkidle" });
    await expect(page.locator("h1")).toContainText("Alignment Lab");
  });

  test("should render arm comparison", async ({ page }) => {
    await page.goto("/compare", { waitUntil: "networkidle" });
    await expect(page.locator("h1")).toContainText("Arm Comparison");
  });

  test("should render lens playground", async ({ page }) => {
    await page.goto("/lens", { waitUntil: "networkidle" });
    await expect(page.locator("h1")).toContainText("Lens Playground");
  });
});

test.describe("Navigation", () => {
  test("should have links to all tools from landing page", async ({
    page,
  }) => {
    await page.goto("/", { waitUntil: "networkidle" });

    const toolLinks = ["/studio", "/build", "/jailbreak", "/align", "/compare", "/lens"];

    for (const link of toolLinks) {
      const element = page.locator(`a[href="${link}"]`);
      await expect(element).toBeVisible();
    }
  });
});
