"use client";

import { ReactNode, useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const AUTH_PREFIX = "/auth";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Allow auth pages without a token.
    if (pathname.startsWith(AUTH_PREFIX)) {
      setReady(true);
      return;
    }

    const token = typeof window !== "undefined" ? window.localStorage.getItem("nixai_token") : null;
    if (!token) {
      router.replace("/auth/login");
      return;
    }

    setReady(true);
  }, [pathname, router]);

  if (!ready) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center text-sm text-slate-400">
        Checking authentication...
      </div>
    );
  }

  return <>{children}</>;
}

