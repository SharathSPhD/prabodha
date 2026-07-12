import { useState, useCallback, useRef } from "react";
import type { SteerRequest, TraceToken, LiveEpisode } from "@/lib/types/steering";

interface UseSSESteerState {
  loading: boolean;
  error: string | null;
  tokens: TraceToken[];
  episode: LiveEpisode | null;
  done: boolean;
}

export function useSSESteer() {
  const [state, setState] = useState<UseSSESteerState>({
    loading: false,
    error: null,
    tokens: [],
    episode: null,
    done: false,
  });
  const abortControllerRef = useRef<AbortController | null>(null);

  const steer = useCallback(async (request: SteerRequest) => {
    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();

    setState({
      loading: true,
      error: null,
      tokens: [],
      episode: null,
      done: false,
    });

    try {
      const response = await fetch("/api/steer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        setState((prev) => ({
          ...prev,
          loading: false,
          // The gateway proxy returns { error, code }; older paths used { message }.
          error: errorData.error || errorData.message || `HTTP ${response.status}`,
        }));
        return;
      }

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setState((prev) => ({ ...prev, loading: false, done: true }));
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines[lines.length - 1];

        for (let i = 0; i < lines.length - 1; i++) {
          const line = lines[i].trim();

          if (line.startsWith("event: token")) {
            const dataLine = lines[++i]?.trim();
            if (dataLine?.startsWith("data: ")) {
              try {
                const token = JSON.parse(dataLine.slice(6));
                setState((prev) => ({
                  ...prev,
                  tokens: [...prev.tokens, token],
                }));
              } catch (e) {
                console.error("Failed to parse token:", e);
              }
            }
          } else if (line.startsWith("event: done")) {
            const dataLine = lines[++i]?.trim();
            if (dataLine?.startsWith("data: ")) {
              try {
                const episode = JSON.parse(dataLine.slice(6));
                setState((prev) => ({
                  ...prev,
                  episode,
                  done: true,
                  loading: false,
                }));
              } catch (e) {
                console.error("Failed to parse episode:", e);
              }
            }
          } else if (line.startsWith("event: error")) {
            const dataLine = lines[++i]?.trim();
            if (dataLine?.startsWith("data: ")) {
              const error = dataLine.slice(6);
              setState((prev) => ({
                ...prev,
                error,
                loading: false,
              }));
            }
          }
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name !== "AbortError") {
        setState((prev) => ({
          ...prev,
          loading: false,
          error: error.message,
        }));
      }
    }
  }, []);

  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setState((prev) => ({ ...prev, loading: false }));
    }
  }, []);

  return { ...state, steer, cancel };
}
