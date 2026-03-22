import axios from "axios"
import { formatError } from "../utils/formatError"

const rawBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
const baseURL = rawBaseUrl && rawBaseUrl.length > 0 ? rawBaseUrl.replace(/\/+$/, "") : "http://127.0.0.1:8000"

export const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json"
  }
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = formatError(err)
    return Promise.reject(new Error(msg))
  }
)
