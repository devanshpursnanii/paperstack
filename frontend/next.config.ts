import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  allowedDevOrigins: [
    "192.168.0.106",
  ],
};

export default nextConfig;
