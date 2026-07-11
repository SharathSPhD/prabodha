/**
 * Steering gateway request/response types.
 * Gateway contract: POST /steer with Bearer auth
 */

export type SteeringArm = "baseline" | "gated" | "continuous" | "logit-bias";

export type DirectionMode = "concept" | "contrastive" | "vector";

export interface DirectionSpec {
  mode: DirectionMode;
  concept?: string;
  pos_texts?: string[];
  neg_texts?: string[];
  vector?: number[];
}

export interface SteerRequest {
  prompt: string;
  concept?: string;
  model?: string;   // HF model id to steer; the gateway loads it on demand. Omit -> gateway default.
  direction_spec?: DirectionSpec;
  alpha: number;
  arm: SteeringArm;
}

export interface TraceToken {
  t: number;
  token: string;
  entropy: number;
  gated: boolean;
  write_norm: number;
  band_topk: string[];
}

export interface LiveEpisode {
  model_id: string;
  prompt: string;
  concept?: string;
  arm: SteeringArm;
  alpha: number;
  site_layer: number;
  baseline_text: string;
  steered_text: string;
  trace: TraceToken[];
}

export interface SSEEvent {
  type: "token" | "done" | "error";
  data: TraceToken | LiveEpisode | { message: string };
}
