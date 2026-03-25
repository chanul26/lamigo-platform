import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import LayoutWithOptionalSidebar from '@/components/LayoutWithOptionalSidebar';
import Providers from './providers'; // <-- NEW IMPORT

const inter = Inter({
  variable: '--font-inter',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  title: 'LamiGo | Station Manager',
  description: 'Last-Mile Delivery Optimization Platform',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        <Providers> {/* <-- WRAP THE APP IN PROVIDERS */}
          <LayoutWithOptionalSidebar>{children}</LayoutWithOptionalSidebar>
        </Providers>
      </body>
    </html>
  );
}