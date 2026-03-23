import { Link, Navigate, Route, Routes } from "react-router-dom"
import SubscribersPage from "./pages/SubscribersPage"
import SubscriberDetailsPage from "./pages/SubscriberDetailsPage"
import DocPage from "./pages/DocPage"

export default function App() {
  return (
    <div className="min-h-screen">
      <div className="mx-auto w-full max-w-6xl px-4 py-8">
        <div className="mb-6 flex items-start justify-between gap-4">
          <div>
            <div className="text-2xl font-semibold tracking-tight">Football Notifications Admin</div>
            <div className="text-sm text-slate-400">Gère les abonnés et leurs équipes (frontend only).</div>
          </div>
          <Link
            to="/doc"
            className="inline-flex rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-500 transition-colors hover:bg-slate-100"
          >
            Doc
          </Link>
        </div>

        <Routes>
          <Route path="/" element={<SubscribersPage />} />
          <Route path="/doc" element={<DocPage />} />
          <Route path="/subscribers/:email" element={<SubscriberDetailsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </div>
  )
}
