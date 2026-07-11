/**
 * API proxy for steer gateway.
 *
 * Forwards requests to the real prabodha steer gateway with authentication.
 * This handler validates the incoming request and proxies it to the gateway,
 * allowing the frontend labs to call the steering endpoint.
 */
import { NextRequest, NextResponse } from "next/server";
import { STEER_GATEWAY_URL, STEER_GATEWAY_SECRET } from "@/lib/config";

export async function POST(request: NextRequest) {
  try {
    // Validate that gateway URL and secret are configured
    if (!STEER_GATEWAY_URL) {
      return NextResponse.json(
        { error: "Gateway not configured (STEER_GATEWAY_URL not set)" },
        { status: 503 }
      );
    }

    if (!STEER_GATEWAY_SECRET) {
      return NextResponse.json(
        { error: "Gateway authentication not configured" },
        { status: 503 }
      );
    }

    // Read the request body
    const body = await request.json();

    // Validate required fields
    if (!body.prompt || !body.concept) {
      return NextResponse.json(
        { error: "Missing required fields: prompt and concept" },
        { status: 400 }
      );
    }

    // Forward to the steer gateway with authentication
    const response = await fetch(`${STEER_GATEWAY_URL}/steer`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${STEER_GATEWAY_SECRET}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json(
        { error: `Gateway error: ${response.statusText}`, details: errorText },
        { status: response.status }
      );
    }

    // Return the streaming response from the gateway
    return new NextResponse(response.body, {
      status: 200,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (error) {
    console.error("Steer API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Lightweight health probe for the client (avoids POSTing an invalid empty request just to
// detect the gateway). Returns { online: boolean } — online only when the gateway /health is 200.
export async function GET() {
  if (!STEER_GATEWAY_URL || !STEER_GATEWAY_SECRET) {
    return NextResponse.json({ online: false, reason: "not_configured" });
  }
  try {
    const res = await fetch(`${STEER_GATEWAY_URL}/health`, {
      headers: { Authorization: `Bearer ${STEER_GATEWAY_SECRET}` },
      signal: AbortSignal.timeout(8000),
    });
    return NextResponse.json({ online: res.ok });
  } catch {
    return NextResponse.json({ online: false, reason: "unreachable" });
  }
}
