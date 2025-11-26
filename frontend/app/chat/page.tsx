"use client";

import { FormEvent, useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { v4 as uuidv4 } from "uuid";

import { AskResponse, SourceInfo, askQuestion, generateSessionTitle } from "@/lib/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceInfo[];
};

type ChatSession = {
  id: string;
  title: string;
  messages: ChatMessage[];
};

export default function ChatPage() {
  const defaultSession = useMemo(
    () => ({
      id: uuidv4(),
      title: "New session",
      messages: [] as ChatMessage[],
    }),
    []
  );

  const [sessions, setSessions] = useState<ChatSession[]>([defaultSession]);
  const [activeSessionId, setActiveSessionId] = useState(defaultSession.id);
  const [prompt, setPrompt] = useState("");
  const [error, setError] = useState<string | null>(null);

  const activeSession = sessions.find((session) => session.id === activeSessionId) ?? sessions[0];

  const askMutation = useMutation({
    mutationFn: (question: string) => askQuestion(question),
    onError: (err: Error) => setError(err.message),
    onSuccess: (response: AskResponse) => {
      setPrompt("");
      setError(null);
      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };

      setSessions((prev) => {
        const next = prev.map((session) => {
          if (session.id !== activeSessionId) return session;
          return {
            ...session,
            messages: [...session.messages, assistantMessage],
          };
        });

        const updatedSession = next.find((session) => session.id === activeSessionId);
        if (updatedSession && updatedSession.title === "New session" && updatedSession.messages.length >= 2) {
          const context = updatedSession.messages
            .map((message) => `${message.role}: ${message.content}`)
            .join("\n");
          titleMutation.mutate({ sessionId: activeSessionId, context });
        }

        return next;
      });
    },
  });

  const titleMutation = useMutation({
    mutationFn: ({ context }: { sessionId: string; context: string }) => generateSessionTitle(context),
    onSuccess: (title, { sessionId }) => {
      setSessions((prev) =>
        prev.map((session) => (session.id === sessionId ? { ...session, title: title || session.title } : session))
      );
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!prompt.trim()) return;
    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: "user",
      content: prompt.trim(),
    };

    setSessions((prev) =>
      prev.map((session) =>
        session.id === activeSessionId
          ? { ...session, messages: [...session.messages, userMessage] }
          : session
      )
    );

    askMutation.mutate(prompt.trim());
  }

  function handleNewSession() {
    const newSession: ChatSession = {
      id: uuidv4(),
      title: "New session",
      messages: [],
    };
    setSessions((prev) => [...prev, newSession]);
    setActiveSessionId(newSession.id);
  }

  return (
    <div className="grid gap-6 md:grid-cols-[220px_minmax(0,1fr)]">
      <aside className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-xl">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Sessions</h2>
          <button
            type="button"
            onClick={handleNewSession}
            className="text-xs font-semibold text-cyan-400 hover:text-cyan-300"
          >
            New
          </button>
        </div>
        <div className="mt-4 space-y-2">
          {sessions.map((session) => (
            <button
              key={session.id}
              onClick={() => setActiveSessionId(session.id)}
              className={`w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                session.id === activeSessionId
                  ? "bg-cyan-500/20 text-white"
                  : "bg-slate-950 text-slate-300 hover:bg-slate-900 hover:text-white"
              }`}
            >
              <p className="font-semibold">{session.title}</p>
              <p className="text-xs text-slate-500">
                {session.messages.length} messages
              </p>
            </button>
          ))}
        </div>
      </aside>

      <section className="flex flex-col overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60 shadow-xl">
        <div className="border-b border-slate-800 px-6 py-4">
          <p className="text-sm font-semibold text-slate-300">{activeSession.title}</p>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4">
          {activeSession.messages.length === 0 ? (
            <p className="text-sm text-slate-400">Start the chat by asking a question.</p>
          ) : (
            <div className="space-y-4">
              {activeSession.messages.map((message) => (
                <div
                  key={message.id}
                  className={`rounded-2xl px-4 py-3 text-sm ${
                    message.role === "user" ? "bg-slate-800 text-slate-200" : "bg-slate-950 text-slate-100"
                  }`}
                >
                  <p className="text-xs uppercase tracking-wide text-slate-500">
                    {message.role === "user" ? "You" : "Assistant"}
                  </p>
                  <p className="mt-1 whitespace-pre-line">{message.content}</p>
                  {message.sources?.length ? (
                    <div className="mt-3 space-y-2 rounded-xl border border-slate-800 bg-slate-950/80 p-3 text-xs">
                      {message.sources.map((source) => (
                        <details key={source.chunk_id} className="rounded-md border border-slate-800/70 bg-slate-900">
                          <summary className="px-2 py-1 text-slate-200">
                            {source.document_name} (chunk {source.chunk_index + 1})
                          </summary>
                          <p className="px-2 py-2 text-slate-400">{source.snippet}</p>
                        </details>
                      ))}
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="border-t border-slate-800 px-6 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Ask anything..."
              className="flex-1 rounded-full border border-slate-800 bg-slate-900 px-4 py-2 text-sm focus:border-cyan-500 focus:outline-none"
            />
            <button
              type="submit"
              className="rounded-full bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
              disabled={askMutation.isPending}
            >
              {askMutation.isPending ? "Thinking..." : "Send"}
            </button>
          </div>
          {error && <p className="mt-2 text-xs text-rose-400">{error}</p>}
        </form>
      </section>
    </div>
  );
}
