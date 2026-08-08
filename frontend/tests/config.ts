import fs from "node:fs"
import path from "node:path"
import { fileURLToPath } from "node:url"
import dotenv from "dotenv"

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const envName = process.env.ENVIRONMENT || "local"
const envPath = path.join(__dirname, "../..", `.env.${envName}`)
if (!fs.existsSync(envPath)) {
  throw new Error(`Missing env file: ${envPath}`)
}
dotenv.config({ path: envPath })

function getEnvVar(name: string): string {
  const value = process.env[name]
  if (!value) {
    throw new Error(`Environment variable ${name} is undefined`)
  }
  return value
}

export const firstSuperuser = getEnvVar("FIRST_SUPERUSER")
export const firstSuperuserPassword = getEnvVar("FIRST_SUPERUSER_PASSWORD")
