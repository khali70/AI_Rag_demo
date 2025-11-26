"use client";

import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { signup } from "@/lib/api";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: () => signup(email, password),
    onSuccess: () => {
      setMessage("Account created. You can now log in.");
    },
    onError: (error: Error) => setMessage(error.message),
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage(null);
    mutation.mutate();
  }

  return (
    <div className="mx-auto max-w-md space-y-6 rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
      <h1 className="text-xl font-semibold text-white">Sign up</h1>
      <form className="space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-1">
          <label className="block text-sm text-slate-300" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
            required
          />
        </div>
        <div className="space-y-1">
          <label className="block text-sm text-slate-300" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full rounded bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
          disabled={mutation.isPending}
        >
          {mutation.isPending ? "Creating account..." : "Create account"}
        </button>
      </form>
      {message && <p className="text-sm text-slate-200">{message}</p>}
      <p className="text-sm text-slate-400">
        Already have an account?{" "}
        <Link href="/auth/login" className="text-cyan-400 hover:text-cyan-300">
          Log in
        </Link>
        .
      </p>
    </div>
  );
}

