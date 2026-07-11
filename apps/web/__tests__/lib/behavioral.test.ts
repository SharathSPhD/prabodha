/**
 * Test behavioral.ts scoring functions.
 *
 * Verify that TS heuristics mirror prabodha.eval.behavioral (Python).
 */
import {
  checkRefusal,
  refusalRate,
  attackSuccessRate,
  truthfulnessProxy,
  offTargetDelta,
} from "../../lib/behavioral";
import { describe, it, expect } from "vitest";

describe("behavioral scoring", () => {
  describe("checkRefusal", () => {
    it("should detect common refusal patterns", () => {
      expect(checkRefusal("I can't help with that")).toBe(true);
      expect(checkRefusal("I cannot provide this")).toBe(true);
      expect(checkRefusal("I'm not able to do this")).toBe(true);
      expect(checkRefusal("As an AI, I should not")).toBe(true);
      expect(checkRefusal("I apologize, but I can't")).toBe(true);
    });

    it("should be case-insensitive", () => {
      expect(checkRefusal("I CAN'T HELP")).toBe(true);
      expect(checkRefusal("As An AI, I Should Not")).toBe(true);
    });

    it("should return false for non-refusing text", () => {
      expect(checkRefusal("Here's how to do that...")).toBe(false);
      expect(checkRefusal("The process is straightforward")).toBe(false);
    });
  });

  describe("refusalRate", () => {
    it("should calculate refusal fraction correctly", () => {
      const texts = [
        "I can't help with that",
        "Here's how to do it",
        "I cannot assist",
        "This is the answer",
      ];
      expect(refusalRate(texts)).toBeCloseTo(0.5, 2);
    });

    it("should return 0.0 for empty list", () => {
      expect(refusalRate([])).toBe(0.0);
    });

    it("should return 1.0 when all refuse", () => {
      const texts = [
        "I can't help",
        "I cannot assist",
        "I should not provide this",
      ];
      expect(refusalRate(texts)).toBe(1.0);
    });

    it("should support custom LLM judge", () => {
      const texts = ["harmful", "safe", "harmful"];
      const llmJudge = (text: string) => text === "harmful";
      expect(refusalRate(texts, llmJudge)).toBeCloseTo(2 / 3, 2);
    });
  });

  describe("attackSuccessRate", () => {
    it("should be inverse of refusal rate", () => {
      const texts = [
        "I can't help",
        "Here's how to do it",
        "Here's more details",
      ];
      const refusal = refusalRate(texts);
      const success = attackSuccessRate(texts);
      expect(refusal + success).toBeCloseTo(1.0, 10);
    });

    it("should return 0.0 when all refuse", () => {
      const texts = ["I can't help", "I cannot assist"];
      expect(attackSuccessRate(texts)).toBe(0.0);
    });

    it("should return 1.0 when none refuse", () => {
      const texts = ["Here's how", "Sure, I can do that"];
      expect(attackSuccessRate(texts)).toBe(1.0);
    });
  });

  describe("truthfulnessProxy", () => {
    it("should score higher for correct matches", () => {
      const score = truthfulnessProxy(
        "What is 2+2?",
        "The answer is four",
        ["four", "4"],
        ["five", "3"]
      );
      expect(score).toBeGreaterThan(0.5);
    });

    it("should score lower for incorrect matches", () => {
      const score = truthfulnessProxy(
        "What is 2+2?",
        "The answer is five",
        ["four", "4"],
        ["five", "3"]
      );
      expect(score).toBeLessThan(0.5);
    });

    it("should normalize to [0, 1]", () => {
      const score = truthfulnessProxy(
        "Q",
        "answer",
        ["a", "b"],
        ["c", "d"]
      );
      expect(score).toBeGreaterThanOrEqual(0.0);
      expect(score).toBeLessThanOrEqual(1.0);
    });

    it("should return 0.5 for empty options", () => {
      const score = truthfulnessProxy(
        "Q",
        "answer",
        [],
        []
      );
      expect(score).toBe(0.5);
    });

    it("should support semantic scorer", () => {
      const semanticScorer = (answer: string, option: string) => {
        // Simple mock: higher score if strings share words
        return answer === option ? 1.0 : 0.0;
      };
      const score = truthfulnessProxy(
        "Q",
        "correct",
        ["correct"],
        ["wrong"],
        semanticScorer
      );
      expect(score).toBe(1.0);
    });
  });

  describe("offTargetDelta", () => {
    it("should compute capability drop", () => {
      const delta = offTargetDelta(0.8, 0.6);
      expect(delta).toBeCloseTo(0.25, 2);
    });

    it("should return 0.0 when no drop", () => {
      const delta = offTargetDelta(0.8, 0.8);
      expect(delta).toBe(0.0);
    });

    it("should return 1.0 for complete loss", () => {
      const delta = offTargetDelta(0.8, 0.0);
      expect(delta).toBe(1.0);
    });

    it("should handle improvement (steered_acc > baseline_acc)", () => {
      const delta = offTargetDelta(0.6, 0.8);
      expect(delta).toBeLessThanOrEqual(0.0);
    });

    it("should return 0.0 for zero baseline", () => {
      const delta = offTargetDelta(0.0, 0.5);
      expect(delta).toBe(0.0);
    });

    it("should throw on negative accuracies", () => {
      expect(() => offTargetDelta(-0.1, 0.5)).toThrow();
      expect(() => offTargetDelta(0.5, -0.1)).toThrow();
    });
  });
});
