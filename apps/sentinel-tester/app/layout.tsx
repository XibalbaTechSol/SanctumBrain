import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sentinel A2A Tester",
  description: "Neural validation for SanctumBrain stack",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased dark">
        {children}
      </body>
    </html>
  );
}
