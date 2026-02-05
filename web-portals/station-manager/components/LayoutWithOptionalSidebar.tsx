'use client';

import { usePathname } from 'next/navigation';
import Sidebar from '@/components/Sidebar';

export default function LayoutWithOptionalSidebar({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isLoginPage = pathname === '/';

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />
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
  );
}
