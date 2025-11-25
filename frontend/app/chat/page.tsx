"use client";

import { useMutation } from "@tanstack/react-query";
import { FormEvent, useState } from "react";

import { AskResponse, SourceInfo, askQuestion } from "@/lib/api";

type ChatMessage =
  | { id: string; role: "user"; content: string }
  | { id: string; role: "assistant"; content: string; sources: SourceInfo[] };

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);

  const generateId = () =>
    typeof crypto !== "undefined" && "randomUUID" in crypto
      ? crypto.randomUUID()
      : Math.random().toString(36).slice(2);

  const askMutation = useMutation<AskResponse, Error, string>({
    mutationFn: (question) => askQuestion(question),
    onSuccess: (data, question) => {
      const userMessage: ChatMessage = {
        id: generateId(),
        role: "user",
        content: question,
      };
      const assistantMessage: ChatMessage = {
        id: generateId(),
        role: "assistant",
        content: data.answer,
        sources: data.sources,
      };
      setHistory((prev) => [...prev, userMessage, assistantMessage]);
      setMessage("");
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) return;
    askMutation.mutate(message.trim());
  }

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
        <h1 className="text-xl font-semibold text-white">Ask the assistant</h1>
        <p className="mt-2 text-sm text-slate-400">Questions will be answered using your uploaded documents.</p>
        <form className="mt-4 flex gap-3" onSubmit={handleSubmit}>
          <input
            type="text"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder="e.g. Summarize the onboarding checklist"
            className="flex-1 rounded border border-slate-700 bg-slate-900 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/60"
          />
          <button
            type="submit"
            className="rounded bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            disabled={askMutation.isPending}
          >
            {askMutation.isPending ? "Thinking..." : "Ask"}
          </button>
        </form>
        {askMutation.isError && (
          <p className="mt-3 text-sm text-rose-400">Error: {askMutation.error?.message ?? "Unknown error"}</p>
        )}
      </section>

      <section className="space-y-4">
        {history.length === 0 ? (
          <p className="text-sm text-slate-400">No messages yet. Ask something to get started.</p>
        ) : (
          history.map((item) =>
            item.role === "user" ? (
              <div key={item.id} className="rounded-lg border border-slate-800 bg-slate-900/60 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">You</p>
                <p className="mt-2 text-sm text-white">{item.content}</p>
              </div>
            ) : (
              <div key={item.id} className="rounded-lg border border-cyan-600/40 bg-slate-900/80 p-4">
                <p className="text-xs uppercase tracking-wide text-cyan-400">Assistant</p>
                <p className="mt-2 whitespace-pre-line text-sm text-slate-100">{item.content}</p>
                {item.sources.length > 0 && (
                  <div className="mt-4 space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Sources</p>
                    {item.sources.map((source) => (
                      <details
                        key={source.chunk_id}
                        className="rounded border border-slate-800 bg-slate-950/60 p-3 text-sm"
                      >
                        <summary className="cursor-pointer text-slate-200">
                          {source.document_name} (chunk {source.chunk_index + 1})
                          {source.score !== undefined && source.score !== null && (
                            <span className="ml-2 text-xs text-slate-500">score {source.score.toFixed(3)}</span>
                          )}
                        </summary>
                        <p className="mt-2 text-slate-300">{source.snippet}</p>
                      </details>
                    ))}
                  </div>
                )}
              </div>
            )
          )
        )}
      </section>
    </div>
  );
}
