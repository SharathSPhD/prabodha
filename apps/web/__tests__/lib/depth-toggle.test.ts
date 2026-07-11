import { describe, it, expect, beforeEach } from "vitest";
import { glossary, getGlossary } from "@/lib/depth-toggle";
import type { DepthMode } from "@/lib/depth-toggle";

describe("Depth Toggle Utilities", () => {
  describe("glossary", () => {
    it("should contain key terms", () => {
      expect(glossary).toHaveProperty("workspace_band");
      expect(glossary).toHaveProperty("sphuratta");
      expect(glossary).toHaveProperty("alpha");
      expect(glossary).toHaveProperty("arm");
      expect(glossary).toHaveProperty("entropy_budget");
    });

    it("should have both explorer and researcher modes for each term", () => {
      Object.values(glossary).forEach((entry) => {
        expect(entry).toHaveProperty("explorer");
        expect(entry).toHaveProperty("researcher");
        expect(typeof entry.explorer).toBe("string");
        expect(typeof entry.researcher).toBe("string");
        expect(entry.explorer.length).toBeGreaterThan(0);
        expect(entry.researcher.length).toBeGreaterThan(0);
      });
    });
  });

  describe("getGlossary", () => {
    it("should return explorer text for explorer mode", () => {
      const result = getGlossary("workspace_band", "explorer");
      expect(result).toBeDefined();
      expect(result).toContain("thinks");
    });

    it("should return researcher text for researcher mode", () => {
      const result = getGlossary("workspace_band", "researcher");
      expect(result).toBeDefined();
      expect(result).toContain("J-space");
    });

    it("should return undefined for unknown terms", () => {
      const result = getGlossary("unknown_term", "explorer");
      expect(result).toBeUndefined();
    });

    it("should handle all terms with both modes", () => {
      const modes: DepthMode[] = ["explorer", "researcher"];

      Object.keys(glossary).forEach((term) => {
        modes.forEach((mode) => {
          const result = getGlossary(term, mode);
          expect(result).toBeDefined();
          expect(result!.length).toBeGreaterThan(0);
        });
      });
    });
  });
});
