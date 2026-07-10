import { describe, it, expect, beforeEach, vi } from "vitest";
import { getMyTier } from "@/lib/account.server";

// Mock Supabase
vi.mock("@/lib/supabase/server", () => ({
  createClient: vi.fn(() => ({
    auth: {
      getUser: vi.fn(async () => ({
        data: { user: { id: "test-id", email: "test@example.com" } },
      })),
    },
    from: vi.fn((table) => ({
      select: vi.fn(async () => ({
        data: { tier: "user" },
      })),
    })),
  })),
}));

describe("account", () => {
  it("getMyTier returns user tier", async () => {
    const tier = await getMyTier();
    expect(tier).toBe("user");
  });
});
