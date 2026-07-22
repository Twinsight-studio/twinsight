import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emits a self-contained server bundle so the Docker runtime stage can ship
  // just .next/standalone instead of the whole node_modules tree.
  output: "standalone",
  turbopack: {
    root: __dirname,
  },
};

export default nextConfig;
