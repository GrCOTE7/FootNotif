import { Link } from "react-router-dom"

export default function DocPage() {
  return (
    <main className="mx-auto w-full max-w-12xl px-0 py-4">
      <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="mb-3 text-2xl font-semibold tracking-tight text-slate-900">Documentation de FootNotif ⚽📩</h1>
        <iframe
          src="/doc.html"
          title="Documentation"
          className="h-[65vh] w-full rounded-md border border-slate-200"
        />
        <div className="mt-5">
          <Link
            to="/"
            className="inline-flex rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-100"
          >
            Retour à l&apos;accueil
          </Link>
        </div>
      </section>
    </main>
  )
}
