import { NextRequest, NextResponse } from "next/server";

export const maxDuration = 120;

export async function POST(req: NextRequest) {
  const backendBase = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const targetUrl = new URL("/api/analyze", backendBase);

  try {
    const headers = new Headers();
    const contentType = req.headers.get("content-type");
    if (contentType) {
      headers.set("content-type", contentType);
    }

    const body = await req.arrayBuffer();

    const response = await fetch(targetUrl.toString(), {
      method: "POST",
      headers,
      body,
    });

    const data = await response.json().catch(() => null);
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("Failed to connect to backend service via binding:", error);
    return NextResponse.json(
      {
        success: false,
        error: {
          code: "BACKEND_UNREACHABLE",
          message: "We couldn't reach the analysis service. Check that the backend is running, then try again.",
        },
      },
      { status: 502 }
    );
  }
}
