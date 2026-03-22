import { api } from "./client"
import { z } from "zod"
import type { Subscriber, Team } from "../types/api"
import { SubscribersResponseSchema, TeamsResponseSchema } from "../types/schemas"

const SubscriberCreateSchema = z.object({
  email: z.string().email(),
  frequency: z.string().min(1)
})

const SubscriptionCreateSchema = z.object({
  email: z.string().email(),
  teams: z.array(z.string().min(1)).min(1)
})

function ensureObjectResponse(data: unknown): void {
  if (typeof data === "string") {
    throw new Error(
      "La reponse API est invalide (texte recu au lieu de JSON). Verifie VITE_API_URL dans football-admin/.env."
    )
  }
}

export async function getSubscribers(): Promise<Subscriber[]> {
  const res = await api.get("/subscribers")
  ensureObjectResponse(res.data)
  const parsed = SubscribersResponseSchema.parse(res.data)
  return parsed.subscribers ?? []
}

export async function createSubscriber(email: string, frequency: string): Promise<void> {
  await api.post("/subscribers", SubscriberCreateSchema.parse({ email, frequency }))
}

export async function deleteSubscriber(email: string): Promise<void> {
  await api.delete(`/subscribers/${encodeURIComponent(email)}`)
}

export async function getSubscriberTeams(email: string): Promise<{ teamNames: string[] }> {
  const res = await api.get(`/subscribers/${encodeURIComponent(email)}/teams`)
  ensureObjectResponse(res.data)
  const parsed = TeamsResponseSchema.parse(res.data)
  const names = parsed.teams.map((t) => (typeof t === "string" ? t : t.name))
  return { teamNames: names }
}

export async function searchTeams(q: string): Promise<Team[]> {
  const res = await api.get("/teams/search", { params: { q } })
  ensureObjectResponse(res.data)
  const parsed = TeamsResponseSchema.parse(res.data)
  return parsed.teams
    .map((t) => (typeof t === "string" ? ({ name: t } as Team) : (t as Team)))
}

export async function addSubscription(email: string, teamName: string): Promise<void> {
  await api.post("/subscriptions", SubscriptionCreateSchema.parse({ email, teams: [teamName] }))
}

export async function removeSubscription(email: string, teamName: string): Promise<void> {
  await api.delete(`/subscriptions/${encodeURIComponent(email)}/${encodeURIComponent(teamName)}`)
}

export async function getTeamByName(teamName: string): Promise<Team | null> {
  const q = teamName.trim()
  if (!q) return null
  try {
    const teams = await searchTeams(q)
    const exact = teams.find((t) => t.name.toLowerCase() === q.toLowerCase())
    return exact ?? teams[0] ?? null
  } catch {
    return null
  }
}
