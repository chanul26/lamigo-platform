'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function TokenProvider() {
  const searchParams = useSearchParams();

  useEffect(() => {
    // Extract JWT token from ?token=xyz in URL
    // TODO: validate token against GET /api/v1/customer/track?token={token}
    const token = searchParams.get('token');

    if (token) {
      // Store token in sessionStorage for use across the page
      sessionStorage.setItem('customer_token', token);
    }
  }, [searchParams]);

  return null; // This component renders nothing — just handles token
}