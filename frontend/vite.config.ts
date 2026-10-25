import path from "path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

const rootDir = import.meta.dirname;

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(rootDir, "./src"),
        "@components": path.resolve(rootDir, "./src/components"),
        "@features": path.resolve(rootDir, "./src/features"),
        "@shared": path.resolve(rootDir, "./src/shared"),
        "@pages": path.resolve(rootDir, "./src/pages"),
      },
    },
    define: {
      "process.env.REACT_APP_API_URL": JSON.stringify(
        env.REACT_APP_API_URL || "http://localhost:8000",
      ),
    },
    server: {
      host: "0.0.0.0",
      port: 3000,
    },
    build: {
      outDir: "build",
    },
  };
});
