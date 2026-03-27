'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import SplashScreen from '@/components/SplashScreen';

const SPLASH_DURATION_MS = 2500;

export default function LoginPage() {
  const router = useRouter();
  const [showSplash, setShowSplash] = useState(true);
  const [adminId, setAdminId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowSplash(false), SPLASH_DURATION_MS);
    return () => clearTimeout(timer);
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const userCredential = await signInWithEmailAndPassword(
        auth,
        adminId.trim(),
        password
      );
      const token = await userCredential.user.getIdToken();
      if (typeof window !== 'undefined') {
        localStorage.setItem('lamigo_station_token', token);
      }
      router.push('/dashboard');
    } catch (err: unknown) {
      const message =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: string }).message)
          : 'Login failed. Please try again.';
      setError(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (showSplash) {
    return <SplashScreen />;
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-6 animate-fade-in"
      style={{ backgroundColor: 'var(--bg-dark)' }}
    >
      <div
        className="w-full max-w-md rounded-[var(--border-radius)] p-8 flex flex-col items-center"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <Image
          src="/assets/logo1.png"
          alt="LamiGo"
          width={120}
          height={120}
          className="mb-6"
          priority
        />

        <form onSubmit={handleSubmit} className="w-full space-y-5">
          <div>
            <label
              htmlFor="adminId"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              Admin ID
            </label>
            <input
              id="adminId"
              type="text"
              value={adminId}
              onChange={(e) => setAdminId(e.target.value)}
              required
              autoComplete="username"
              className="w-full px-4 py-3 rounded-[var(--border-radius-sm)] text-sm transition-[border-color,box-shadow] outline-none focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30"
              style={{
                backgroundColor: 'var(--bg-dark)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
              placeholder="Enter your Admin ID (email)"
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="block text-sm font-medium mb-2"
              style={{ color: 'var(--text-secondary)' }}
            >
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              className="w-full px-4 py-3 rounded-[var(--border-radius-sm)] text-sm transition-[border-color,box-shadow] outline-none focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30"
              style={{
                backgroundColor: 'var(--bg-dark)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
              }}
              placeholder="Enter your password"
            />
          </div>

          {error && (
            <p
              className="text-sm"
              style={{ color: 'var(--status-failed)' }}
            >
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-[var(--border-radius)] font-semibold text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
            style={{
              backgroundColor: 'var(--primary-blue)',
              color: 'white',
            }}
            onMouseEnter={(e) => {
              if (!isSubmitting) {
                e.currentTarget.style.backgroundColor = 'var(--primary-blue-hover)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--primary-blue)';
            }}
          >
            {isSubmitting ? 'Signing in…' : 'Login'}
          </button>
        </form>

        <a
          href="#"
          className="mt-4 text-sm hover:underline"
          style={{ color: 'var(--text-secondary)' }}
          onClick={(e) => {
            e.preventDefault();
            // Forgot password flow can be wired later
          }}
        >
          Forgot Password?
        </a>
      </div>
    </div>
  );
}
