import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/auth/AuthProvider';

export const metadata: Metadata = {
  title: {
    default: 'Workforce Intelligence',
    template: '%s | Workforce Intelligence',
  },
  description: 'Executive Workforce Intelligence Platform — Apex Software Solutions',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
