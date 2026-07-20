import { apiFetch } from "@/lib/api/client";

// Mirrors backend/app/modules/stocks/schemas.py::QuoteResponse. Backend
// Pydantic models use CamelModel (alias_generator=to_camel), so the wire
// format is camelCase — keep this type in sync, no mapping layer needed.
export interface QuoteResponse {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  updatedAt: string;
}

export function getQuote(symbol: string): Promise<QuoteResponse> {
  return apiFetch<QuoteResponse>(`/api/v1/stocks/${symbol}/quote`);
}
