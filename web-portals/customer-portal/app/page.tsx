'use client';

import { useEffect, useState } from 'react';
import SplashScreen from '@/components/SplashScreen';
import ComingSoonPage from '@/components/ComingSoonPage';

const SPLASH_DURATION_MS = 2000;

export default function Home() {
  const [showSplash, setShowSplash] = useState(true);

  useEffect(() => {
    const t = setTimeout(() => setShowSplash(false), SPLASH_DURATION_MS);
    return () => clearTimeout(t);
  }, []);

  return (
    <>
      {showSplash && <SplashScreen />}
      <ComingSoonPage />
    </>
  );
}
