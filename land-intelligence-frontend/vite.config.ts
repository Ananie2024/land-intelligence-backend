import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [
    react(),
  ],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  server: {
    port: 5173,
    open: true,

    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },

  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          // Core React ecosystem - loaded on most pages
          if (
            id.includes("node_modules") &&
            (id.includes("react/") ||
              id.includes("react-dom/") ||
              id.includes("react-router-dom") ||
              id.includes("@tanstack/react-query") ||
              id.includes("zustand") ||
              id.includes("axios") ||
              id.includes("react-hook-form") ||
              id.includes("@hookform/resolvers") ||
              id.includes("zod") ||
              id.includes("clsx") ||
              id.includes("lucide-react"))
          ) {
            return "react-vendor";
          }

          // Chart.js - typically only used in specific dashboard/analytics pages
          if (
            id.includes("node_modules") &&
            (id.includes("chart.js") || id.includes("react-chartjs-2"))
          ) {
            return "charts";
          }

          // Leaflet - typically only used in GIS/mapping pages
          if (
            id.includes("node_modules") &&
            (id.includes("leaflet") || id.includes("react-leaflet"))
          ) {
            return "maps";
          }

          // Return undefined for app code (default behavior)
          return undefined;
        },
      },
    },
  },
});
