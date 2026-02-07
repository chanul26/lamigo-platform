export default function ComingSoonPage() {
  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)]">
      <main className="mx-auto flex min-h-screen w-full max-w-lg flex-col items-center justify-center px-4 py-8">
        <div className="rounded-2xl border border-[var(--border-color)] bg-white p-8 text-center shadow-sm">
          <h1 className="mb-2 text-2xl font-semibold text-[var(--text-primary)]">
            Still Implementing
          </h1>
          <p className="text-[var(--text-secondary)]">
            We&apos;re still building this page. Check back later.
          </p>
        </div>
      </main>
    </div>
  );
}
