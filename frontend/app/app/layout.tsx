'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { SessionProvider } from '@/contexts/SessionContext';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  useEffect(() => {
    // Check if token exists
    const token = localStorage.getItem('paperstack_token');
    
    if (!token) {
      // No token, redirect to login
      router.push('/');
      return;
    }

    // Add session cleanup on browser close
    const handleBeforeUnload = async () => {
      const sessionId = localStorage.getItem('paperstack_session_id');
      if (sessionId) {
        // Best effort - might not complete if browser closes too fast
        navigator.sendBeacon(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/session/${sessionId}`,
          JSON.stringify({ _method: 'DELETE' })
        );
      }
      // Clear auth state on browser close
      localStorage.removeItem('paperstack_token');
      localStorage.removeItem('paperstack_session_id');
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [router]);

  return <SessionProvider>{children}</SessionProvider>;
}
