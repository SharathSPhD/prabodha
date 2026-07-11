import { NextRequest, NextResponse } from "next/server";
import type { SteerRequest } from "@/lib/types/steering";

/**
 * POST /api/steer
 * Proxy to the steering gateway with SSE forwarding.
 * The gateway is configured via environment variables:
 * - STEER_GATEWAY_URL: the base URL of the steering gateway
 * - STEER_GATEWAY_SECRET: Bearer token for authentication
 */
export async function POST(req: NextRequest) {
  try {
    const gatewayUrl = process.env.STEER_GATEWAY_URL;
    const gatewaySecret = process.env.STEER_GATEWAY_SECRET;

    if (!gatewayUrl || !gatewaySecret) {
      return NextResponse.json(
        {
          error: "Gateway not configured",
          message:
            "Steering gateway is offline or not configured. Showing a recorded run instead.",
        },
        { status: 503 }
      );
    }

    const body: SteerRequest = await req.json();

    // Forward to gateway
    const gatewayRes = await fetch(`${gatewayUrl}/steer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${gatewaySecret}`,
      },
      body: JSON.stringify(body),
    });

    if (!gatewayRes.ok) {
      return NextResponse.json(
        { error: `Gateway error: ${gatewayRes.statusText}` },
        { status: gatewayRes.status }
      );
    }

    // Stream the SSE response directly
    return new NextResponse(gatewayRes.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (error) {
    console.error("Steering error:", error);
    return NextResponse.json(
      {
        error: "Steering request failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 }
    );
  }
}
