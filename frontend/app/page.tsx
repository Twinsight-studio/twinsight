// Re-fetch backend health on every request (not baked into a static
// prerender) so this reflects live status.
export const dynamic = 'force-dynamic'

async function checkBackendHealth(): Promise<string> {
  // Server components run inside the frontend container, where the API is
  // reachable over the compose network (API_BASE_URL=http://api:8080).
  // `localhost` there would mean this container itself. On the host (`next
  // dev`) API_BASE_URL is unset, so we fall back to the browser-facing URL.
  const apiBaseUrl = process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL
  if (!apiBaseUrl) return 'API base URL not configured'

  try {
    const res = await fetch(`${apiBaseUrl}/health`, { cache: 'no-store' })
    const data = await res.json()
    return JSON.stringify(data)
  } catch (err) {
    return `unreachable: ${err instanceof Error ? err.message : String(err)}`
  }
}

export default async function HomePage() {
  const backendHealth = await checkBackendHealth()

  return (
    <main className="flex flex-1 flex-col items-center justify-center gap-2 p-16">
      <h1 className="text-2xl font-semibold">TwInsight</h1>
      <p className="text-muted-foreground">架構骨架已就位，頁面內容待補。</p>
      <p className="text-sm">Backend health: {backendHealth}</p>
    </main>
  )
}
