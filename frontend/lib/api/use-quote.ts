"use client";

import { useQuery } from "@tanstack/react-query";

import { getQuote } from "@/lib/api/quote";

// Matches the backend cache TTL (quote:{symbol}, 30s) — see
// backend/app/modules/stocks/service.py.
const QUOTE_POLL_INTERVAL_MS = 30_000;

export function useQuote(symbol: string) {
  return useQuery({
    queryKey: ["quote", symbol],
    queryFn: () => getQuote(symbol),
    refetchInterval: QUOTE_POLL_INTERVAL_MS,
  });
}
