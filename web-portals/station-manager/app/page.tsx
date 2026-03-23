'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import {
  signInWithPhoneNumber,
  RecaptchaVerifier,
  ConfirmationResult,
  signOut,
} from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { logoutUser } from '@/lib/api';
import SplashScreen from '@/components/SplashScreen';

const SPLASH_DURATION_MS = 2500;
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

function formatPhoneNumber(countryCode: string, number: string): string {
  const cleaned = number.replace(/\D/g, '');
  return `${countryCode}${cleaned}`;
}

export default function LoginPage() {
  const router = useRouter();

  const [showSplash, setShowSplash] = useState(true);
  const [step, setStep] = useState<'phone' | 'otp'>('phone');

  const [countryCode, setCountryCode] = useState('+94');
  const [phoneNumber, setPhoneNumber] = useState('');

  const [otp, setOtp] = useState('');
  const [confirmationResult, setConfirmationResult] =
    useState<ConfirmationResult | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const recaptchaContainerRef = useRef<HTMLDivElement>(null);
  const recaptchaVerifierRef = useRef<RecaptchaVerifier | null>(null);

  // ── splash timer ──────────────────────────────────────────────
  useEffect(() => {
    const t = setTimeout(() => setShowSplash(false), SPLASH_DURATION_MS);
    return () => clearTimeout(t);
  }, []);

  // ── init invisible reCAPTCHA once splash is gone ─────────────
  useEffect(() => {
    if (showSplash) return;

    if (recaptchaVerifierRef.current) {
      recaptchaVerifierRef.current.clear();
      recaptchaVerifierRef.current = null;
    }

    if (!recaptchaContainerRef.current) return;

    recaptchaVerifierRef.current = new RecaptchaVerifier(
      auth,
      recaptchaContainerRef.current,
      { size: 'invisible' }
    );

    return () => {
      if (recaptchaVerifierRef.current) {
        recaptchaVerifierRef.current.clear();
        recaptchaVerifierRef.current = null;
      }
    };
  }, [showSplash]);

  // ── send OTP ──────────────────────────────────────────────────
  async function handleSendOtp(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const fullPhone = formatPhoneNumber(countryCode, phoneNumber);

      if (!recaptchaVerifierRef.current) {
        throw new Error('reCAPTCHA not initialised. Please refresh the page.');
      }

      const result = await signInWithPhoneNumber(
        auth,
        fullPhone,
        recaptchaVerifierRef.current
      );

      setConfirmationResult(result);
      setSuccessMsg(`OTP sent to ${fullPhone}`);
      setStep('otp');
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: string }).message)
          : 'Failed to send OTP. Please try again.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  // ── verify OTP + role check + backend login ───────────────────
  async function handleVerifyOtp(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (!confirmationResult) {
        throw new Error('No confirmation result. Please request a new OTP.');
      }

      // 1. Confirm OTP with Firebase
      const userCredential = await confirmationResult.confirm(otp.trim());
      const idToken = await userCredential.user.getIdToken();

      // 2. Call /me to check role before we do anything else
      const meRes = await fetch(`${API_BASE_URL}/auth/me`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
      });

      if (!meRes.ok) {
        const data = await meRes.json().catch(() => ({}));
        throw new Error(
          data?.detail || `Authentication failed: ${meRes.status} ${meRes.statusText}`
        );
      }

      const profile = await meRes.json();

      // 3. Role guard — only STATION_MANAGER is allowed here
      if (profile.role !== 'STATION_MANAGER') {
        // Call backend logout to clear FCM token + revoke session, then Firebase signOut
        await logoutUser(idToken);
        await signOut(auth);
        throw new Error(
          `Access denied. This portal is for Station Managers only. Your account role is "${profile.role}".`
        );
      }

      // 4. Role is valid → call login endpoint (records last_access_at, clears fcm_token)
      const loginRes = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({ fcm_token: null }),
      });

      if (!loginRes.ok) {
        const data = await loginRes.json().catch(() => ({}));
        throw new Error(
          data?.detail || `Backend error: ${loginRes.status} ${loginRes.statusText}`
        );
      }

      // 5. Persist token and go to dashboard
      if (typeof window !== 'undefined') {
        localStorage.setItem('lamigo_station_token', idToken);
      }

      router.push('/dashboard');
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'message' in err
          ? String((err as { message: string }).message)
          : 'Verification failed. Please try again.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  }

  // ── resend / change number ────────────────────────────────────
  function handleResend() {
    setStep('phone');
    setOtp('');
    setError(null);
    setSuccessMsg(null);
    setConfirmationResult(null);
  }

  // ── render ────────────────────────────────────────────────────
  if (showSplash) return <SplashScreen />;

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center p-6 animate-fade-in"
      style={{ backgroundColor: 'var(--bg-dark)' }}
    >
      {/* Invisible reCAPTCHA anchor */}
      <div ref={recaptchaContainerRef} />

      <div
        className="w-full max-w-md rounded-[var(--border-radius)] p-8 flex flex-col items-center"
        style={{
          backgroundColor: 'var(--card-bg)',
          border: '1px solid var(--border-color)',
        }}
      >
        <Image
          src="/assets/LamiGo_Logo_Light.svg"
          alt="LamiGo"
          width={160}
          height={60}
          className="mb-8"
          priority
        />

        {/* ── STEP 1: Phone Number ── */}
        {step === 'phone' && (
          <form onSubmit={handleSendOtp} className="w-full space-y-5">
            <div>
              <label
                htmlFor="phone"
                className="block text-sm font-medium mb-2"
                style={{ color: 'var(--text-secondary)' }}
              >
                Phone Number
              </label>

              <div className="flex gap-2">
                <input
                  id="countryCode"
                  type="text"
                  value={countryCode}
                  onChange={(e) => setCountryCode(e.target.value)}
                  className="w-20 px-3 py-3 rounded-[var(--border-radius-sm)] text-sm text-center outline-none focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30 transition-[border-color,box-shadow]"
                  style={{
                    backgroundColor: 'var(--bg-dark)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                  }}
                  placeholder="+94"
                />

                <input
                  id="phone"
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  required
                  autoComplete="tel"
                  className="flex-1 px-4 py-3 rounded-[var(--border-radius-sm)] text-sm outline-none focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30 transition-[border-color,box-shadow]"
                  style={{
                    backgroundColor: 'var(--bg-dark)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                  }}
                  placeholder="771234567"
                />
              </div>
            </div>

            {error && (
              <p
                className="text-sm rounded-[var(--border-radius-sm)] px-3 py-2"
                style={{
                  color: 'var(--status-failed)',
                  backgroundColor: 'var(--status-failed-bg)',
                }}
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={isSubmitting || !phoneNumber}
              className="w-full py-3 rounded-[var(--border-radius)] font-semibold text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ backgroundColor: 'var(--primary-blue)', color: 'white' }}
              onMouseEnter={(e) => {
                if (!isSubmitting)
                  e.currentTarget.style.backgroundColor =
                    'var(--primary-blue-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--primary-blue)';
              }}
            >
              {isSubmitting ? 'Sending OTP…' : 'Send OTP'}
            </button>
          </form>
        )}

        {/* ── STEP 2: OTP Verification ── */}
        {step === 'otp' && (
          <form onSubmit={handleVerifyOtp} className="w-full space-y-5">
            {successMsg && (
              <p
                className="text-sm text-center rounded-[var(--border-radius-sm)] px-3 py-2"
                style={{
                  color: 'var(--status-delivered)',
                  backgroundColor: 'var(--status-delivered-bg)',
                }}
              >
                {successMsg}
              </p>
            )}

            <div>
              <label
                htmlFor="otp"
                className="block text-sm font-medium mb-2"
                style={{ color: 'var(--text-secondary)' }}
              >
                Enter OTP
              </label>
              <input
                id="otp"
                type="text"
                inputMode="numeric"
                maxLength={6}
                value={otp}
                onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
                required
                autoComplete="one-time-code"
                className="w-full px-4 py-3 rounded-[var(--border-radius-sm)] text-sm text-center tracking-[0.5em] outline-none focus:border-[var(--primary-blue)] focus:ring-2 focus:ring-[var(--primary-blue)] focus:ring-opacity-30 transition-[border-color,box-shadow]"
                style={{
                  backgroundColor: 'var(--bg-dark)',
                  border: '1px solid var(--border-color)',
                  color: 'var(--text-primary)',
                }}
                placeholder="• • • • • •"
              />
            </div>

            {error && (
              <p
                className="text-sm rounded-[var(--border-radius-sm)] px-3 py-2"
                style={{
                  color: 'var(--status-failed)',
                  backgroundColor: 'var(--status-failed-bg)',
                }}
              >
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={isSubmitting || otp.length < 6}
              className="w-full py-3 rounded-[var(--border-radius)] font-semibold text-sm transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
              style={{ backgroundColor: 'var(--primary-blue)', color: 'white' }}
              onMouseEnter={(e) => {
                if (!isSubmitting)
                  e.currentTarget.style.backgroundColor =
                    'var(--primary-blue-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--primary-blue)';
              }}
            >
              {isSubmitting ? 'Verifying…' : 'Verify & Login'}
            </button>

            <button
              type="button"
              onClick={handleResend}
              className="w-full text-sm hover:underline"
              style={{ color: 'var(--text-secondary)' }}
            >
              Resend OTP / Change number
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
