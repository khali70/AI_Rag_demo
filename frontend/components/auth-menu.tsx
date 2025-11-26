"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { logout } from "@/lib/api";

export function AuthMenu() {
  const router = useRouter();
  const pathname = usePathname();
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    setHasToken(Boolean(window.localStorage.getItem("nixai_token")));
  }, [pathname]);

  async function handleLogout() {
    logout();
    setHasToken(false);
    router.replace("/auth/login");
  }

  if (!hasToken) {
    return (
      <Link href="/auth/login" className="text-slate-300 hover:text-white">
        Login
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="text-slate-300 hover:text-white"
    >
      Logout
    </button>
  );
}
