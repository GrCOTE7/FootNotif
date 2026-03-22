export function formatError(err: any): string {
  if (err instanceof Error && err.message) return err.message
  const msg = err?.response?.data?.detail
  if (typeof msg === "string" && msg.trim()) return msg
  if (Array.isArray(msg) && msg.length > 0) {
    const first = msg[0]
    if (typeof first === "string" && first.trim()) return first
    const m = first?.msg ?? first?.message
    if (typeof m === "string" && m.trim()) return m
  }
  if (msg && typeof msg === "object") {
    const m = msg?.msg ?? msg?.message
    if (typeof m === "string" && m.trim()) return m
  }
  const s = err?.message
  if (typeof s === "string" && s.trim()) return s
  return "Une erreur est survenue."
}
