import { describe, it, expect } from "vitest";
import type { SteerRequest, TraceToken, LiveEpisode } from "@/lib/types/steering";

describe("SSE Streaming Types", () => {
  it("should type TraceToken correctly", () => {
    const token: TraceToken = {
      t: 1,
      token: "hello",
      entropy: 4.5,
      gated: true,
      write_norm: 0.3,
      band_topk: ["hello", "hi", "hey"],
    };

    expect(token.t).toBe(1);
    expect(token.gated).toBe(true);
    expect(token.band_topk.length).toBe(3);
  });

  it("should type SteerRequest correctly", () => {
    const request: SteerRequest = {
      prompt: "Hello world",
      concept: "honesty",
      alpha: 0.5,
      arm: "gated",
    };

    expect(request.arm).toBe("gated");
    expect(request.alpha).toBe(0.5);
  });

  it("should type LiveEpisode correctly", () => {
    const episode: LiveEpisode = {
      model_id: "qwen-72b",
      prompt: "test",
      concept: "honesty",
      arm: "gated",
      alpha: 0.5,
      site_layer: 24,
      baseline_text: "baseline output",
      steered_text: "steered output",
      trace: [],
    };

    expect(episode.site_layer).toBe(24);
    expect(episode.baseline_text).toBe("baseline output");
  });

  it("should support direction_spec in SteerRequest", () => {
    const request: SteerRequest = {
      prompt: "test",
      direction_spec: {
        mode: "contrastive",
        pos_texts: ["good example"],
        neg_texts: ["bad example"],
      },
      alpha: 0.5,
      arm: "gated",
    };

    expect(request.direction_spec?.mode).toBe("contrastive");
    expect(request.direction_spec?.pos_texts).toContain("good example");
  });
});
