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

  // If on the login page returns the children without Sidebar
  if (isLoginPage) {
    return <>{children}</>;
  }

  // For all other pages the Sidebar and the Main content area
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main
        className="flex-1 min-h-screen transition-all duration-200"
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
