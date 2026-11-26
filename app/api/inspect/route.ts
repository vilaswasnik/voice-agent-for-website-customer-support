import { NextResponse } from "next/server";

export const runtime = "nodejs";

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return NextResponse.json(
      { detail: "Send a JSON request with a website URL." },
      { status: 400 },
    );
  }

  if (
    typeof payload !== "object" ||
    payload === null ||
    !("url" in payload) ||
    typeof payload.url !== "string" ||
    payload.url.trim().length === 0 ||
    payload.url.length > 2048
  ) {
    return NextResponse.json(
      { detail: "Enter a website address no longer than 2048 characters." },
      { status: 400 },
    );
  }

  const serviceUrl = process.env.AGENT_SERVICE_URL ?? "http://127.0.0.1:8000";
  let response: Response;
  try {
    response = await fetch(`${serviceUrl.replace(/\/$/, "")}/inspect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: payload.url.trim() }),
      cache: "no-store",
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    return NextResponse.json(
      { detail: "The website inspector is unavailable. Please try again shortly." },
      { status: 503 },
    );
  }

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    return NextResponse.json(
      { detail: "The website inspector returned an invalid response." },
      { status: 502 },
    );
  }

  return NextResponse.json(result, { status: response.status });
}
