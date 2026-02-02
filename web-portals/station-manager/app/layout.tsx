import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/Sidebar';

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'LamiGo | Station Manager',
  description: 'Last-Mile Delivery Optimization Platform - Station Manager Portal',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        <div className="flex min-h-screen">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <main
            className="flex-1 min-h-screen"
            style={{
              marginLeft: 'var(--sidebar-width)',
              backgroundColor: 'var(--bg-dark)',
            }}
          >
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
