import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Serve at /admin path for Context Forge integration
  basePath: "/admin",

  // Standalone output for Docker deployment
  output: "standalone",

  // API proxy configuration
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NEXT_PUBLIC_API_URL || "http://gateway:8030/api/:path*",
      },
    ];
  },
};

export default nextConfig;
