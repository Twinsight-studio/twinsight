# TwInsight frontend

Next.js app. Root-level [`README.md`](../README.md) has the full monorepo dev/deploy guide;
this file just covers frontend-only commands.

```bash
npm install
npm run dev             # http://localhost:3000
npm run lint
npm run typecheck
npm run test
npm run build            # next build
npm run opennext:build   # OpenNext build for Cloudflare Workers
npm run preview          # opennext build + wrangler local preview
npm run deploy           # opennext build + wrangler deploy
```
