'use client';

import Image from 'next/image';

export default function SplashScreen() {
  return (
    <div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white"
      aria-hidden="true"
    >
      <div className="flex flex-col items-center gap-6">
        <Image
          src="/assets/LamiGo_Logo_Light.svg"
          alt="LamiGo"
          width={500}
          height={500}
          className="animate-pulse"
          priority
        />
        <span className="text-2xl font-semibold tracking-tight text-gray-800">
          Last Mile Delivery Optimisation Platform
        </span>
      </div>
    </div>
  );
}
