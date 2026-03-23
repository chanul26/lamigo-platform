'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      // Navigate to the tracking sub-folder while keeping the token
      router.push(`/track?token=${token}`);
    }
  }, [token, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <div className="text-center">
        <div className="h-10 w-10 animate-spin border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-500 animate-pulse">Redirecting to your delivery status...</p>
      </div>
    </div>
  );
}