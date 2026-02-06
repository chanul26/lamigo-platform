import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import LayoutWithOptionalSidebar from '@/components/LayoutWithOptionalSidebar';

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
        <LayoutWithOptionalSidebar>{children}</LayoutWithOptionalSidebar>
      </body>
    </html>
  );
}
