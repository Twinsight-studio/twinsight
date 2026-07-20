import { defineCloudflareConfig } from "@opennextjs/cloudflare";

// TODO: add incrementalCache / tagCache / queue overrides once we need
// ISR/ on Cloudflare (KV/D1/R2 bindings). Defaults are fine for v1.
export default defineCloudflareConfig();
