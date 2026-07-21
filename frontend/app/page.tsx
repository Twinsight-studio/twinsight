// API_BASE_URL is a Cloudflare Workers runtime var (wrangler.jsonc), not
// known at Next.js build time — force per-request rendering so it's read
// fresh instead of baked into a static prerender.
export const dynamic = "force-dynamic";

async function checkBackendHealth(): Promise<string> {
  const apiBaseUrl = process.env.API_BASE_URL;
  if (!apiBaseUrl) return "API_BASE_URL not configured";

  try {
    const res = await fetch(`${apiBaseUrl}/health`, { cache: "no-store" });
    const data = await res.json();
    return JSON.stringify(data);
  } catch (err) {
    return `unreachable: ${err instanceof Error ? err.message : String(err)}`;
  }
}

export default async function Home() {
  const backendHealth = await checkBackendHealth();

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-2 p-16">
      <h1 className="text-2xl font-semibold">TwInsight</h1>
      <p className="text-muted-foreground">架構骨架已就位，頁面內容待補。</p>
      <p className="text-sm">Backend health: {backendHealth}</p>
    </main>
  );
}
