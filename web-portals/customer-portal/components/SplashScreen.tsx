'use client';

import Image from 'next/image';

export default function SplashScreen() {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#121212]"
      aria-hidden="true"
    >
      <Image
        src="/assets/LamiGo_Logo_Dark.svg"
        alt="LamiGo"
        width={280}
        height={82}
        className="animate-pulse"
        priority
      />
    </div>
  );
}
