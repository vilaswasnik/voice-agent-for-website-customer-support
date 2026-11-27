export const runtime = "nodejs";

export async function POST(request: Request) {
  let payload: unknown;
  try {
    payload = await request.json();
  } catch {
    return Response.json(
      { detail: "Send a JSON request with a website URL and a search query." },
      { status: 400 },
    );
  }
  if (typeof payload !== "object" || payload === null) {
    return Response.json(
      { detail: "Send a JSON request with a website URL and a search query." },
      { status: 400 },
    );
  }
  const body = payload as Record<string, unknown>;
  const url = typeof body.url === "string" ? body.url.trim() : "";
  const query = typeof body.query === "string" ? body.query.trim() : "";
  if (!url) {
    return Response.json({ detail: "Enter a website address." }, { status: 400 });
  }
  if (url.length > 2048) {
    return Response.json(
      { detail: "Enter a website address no longer than 2048 characters." },
      { status: 400 },
    );
  }
  if (!query) {
    return Response.json({ detail: "Enter something to search for." }, { status: 400 });
  }
  if (query.length > 500) {
    return Response.json(
      { detail: "Enter a search query no longer than 500 characters." },
      { status: 400 },
    );
  }
  const agentServiceUrl =
    process.env.AGENT_SERVICE_URL ?? "http://127.0.0.1:8000";
  let response: Response;
  try {
    response = await fetch(`${agentServiceUrl}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, query }),
      cache: "no-store",
      signal: AbortSignal.timeout(60_000),
    });
  } catch {
    return Response.json(
      { detail: "The website search is unavailable. Please try again shortly." },
      { status: 503 },
    );
  }
  let result: unknown;
  try {
    result = await response.json();
  } catch {
    return Response.json(
      { detail: "The website search returned an invalid response." },
      { status: 502 },
    );
  }
  return Response.json(result, { status: response.status });
}
