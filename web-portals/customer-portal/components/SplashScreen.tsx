'use client';

import Image from 'next/image';

export default function SplashScreen() {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#121212]"
      aria-hidden="true"
    >
      <div className="flex flex-col items-center gap-4">
        <Image
          src="/assets/LamiGo_Logo_Dark.svg"
          alt="LamiGo"
          width={280}
          height={82}
          className="animate-pulse"
          priority
        />

        <span className="text-lg font-medium tracking-tight text-gray-300">
          Last Mile Delivery Optimisation Platform
        </span>
        <span className="text-sm font-medium tracking-tight text-gray-400">
          Customer Portal
        </span>
      </div>
    </div>
  );
}
