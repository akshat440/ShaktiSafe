import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'IntelliTrace — Cross-Channel Mule Detection System',
  description: 'Real-time GNN-based mule account detection. Indian Bank × VIT Chennai — PSBs Hackathon 2026',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet" />
      </head>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
