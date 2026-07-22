# TwInsight frontend — production Next.js server (next build + standalone).
# Not the dev server: `make dev-frontend` still runs `next dev` on the host
# when you want hot reload.
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# NEXT_PUBLIC_* is inlined into the client bundle at build time, so the
# browser-facing API URL has to be known here. The browser runs on the host,
# so this is the published host port — NOT the compose network name.
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
RUN npm run build

FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
# standalone output already bundles the server + its runtime deps; static
# assets and public/ are not included in it and must be copied alongside.
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
