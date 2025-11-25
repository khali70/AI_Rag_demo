import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";
import { Providers } from "@/components/providers";

export const metadata: Metadata = {
  title: "NixAI",
  description: "Upload docs and chat with a retrieval-augmented assistant.",
};

const navItems = [
  { href: "/documents", label: "Documents" },
  { href: "/chat", label: "Chat" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>
          <div className="min-h-screen bg-slate-950 text-slate-100">
            <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
              <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
                <Link href="/documents" className="text-lg font-semibold text-cyan-400">
                  NixAI Dashboard
                </Link>
                <nav className="flex gap-4 text-sm">
                  {navItems.map((item) => (
                    <Link key={item.href} href={item.href} className="text-slate-300 hover:text-white">
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </div>
            </header>
            <main className="mx-auto max-w-5xl px-4 py-8">{children}</main>
          </div>
        </Providers>
      </body>
    </html>
  );
}
