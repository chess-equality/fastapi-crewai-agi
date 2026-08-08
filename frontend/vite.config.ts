import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import dotenv from "dotenv"
import tailwindcss from "@tailwindcss/vite"
import { tanstackRouter } from "@tanstack/router-plugin/vite"
import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// Load the environment-specific .env file from the repo root.
const envName = process.env.ENVIRONMENT || "local"
const rootDir = path.resolve(__dirname, "..")
const envPath = path.resolve(rootDir, `.env.${envName}`)
if (!fs.existsSync(envPath)) {
  throw new Error(`Missing env file: ${envPath}`)
}
const parsed = dotenv.parse(fs.readFileSync(envPath, "utf8"))

const define: Record<string, string> = {}
for (const [key, value] of Object.entries(parsed)) {
  if (key.startsWith("VITE_")) {
    // Allow build-time env vars (e.g. VITE_API_URL build arg) to override
    // the file, but treat an empty string as unset.
    const envValue = process.env[key] && process.env[key] !== "" ? process.env[key] : value
    define[`import.meta.env.${key}`] = JSON.stringify(envValue)
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  envDir: false,
  build: {
    outDir: "../backend/app/frontend",
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define,
  plugins: [
    tanstackRouter({
      target: "react",
      autoCodeSplitting: true,
    }),
    react(),
    tailwindcss(),
  ],
})
