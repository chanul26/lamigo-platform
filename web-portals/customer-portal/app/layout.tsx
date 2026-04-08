'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import "./globals.css";

// 🛡️ TokenGate: Extracts JWT from SMS link and validates access
function TokenGate({ children }: { children: React.ReactNode }) {
  const searchParams = useSearchParams();
  const [isValidating, setIsValidating] = useState(true);
  const token = searchParams.get('token');

  useEffect(() => {
    // Artificial delay to simulate JWT validation
    const timer = setTimeout(() => setIsValidating(false), 500);
    return () => clearTimeout(timer);
  }, [token]);

  if (isValidating) {
    return (
      <div className="flex h-screen items-center justify-center bg-white font-sans">
        <div className="flex flex-col items-center gap-3">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="text-slate-500 font-medium">Verifying Secure Link...</p>
        </div>
      </div>
    );
  }

  // If no token exists in the URL, block the portal content
  if (!token) {
    return (
      <div className="flex h-screen flex-col items-center justify-center bg-slate-50 p-6 text-center">
        <div className="bg-white p-10 rounded-[2.5rem] shadow-2xl border border-red-50 max-w-sm">
          <div className="bg-red-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-2xl">⚠️</span>
          </div>
          <h1 className="text-2xl font-black text-slate-900 mb-2">Access Denied</h1>
          <p className="text-slate-500 text-sm leading-relaxed">
            This tracking portal requires a unique link sent via SMS. 
            Please use the link provided in your delivery message.
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-blue-100">
        <Suspense fallback={<div className="p-10 text-center">Loading LamiGo...</div>}>
          <TokenGate>
            <main className="min-h-screen bg-slate-50 text-slate-900">
              {children}
            </main>
          </TokenGate>
        </Suspense>
      </body>
    </html>
  );
}