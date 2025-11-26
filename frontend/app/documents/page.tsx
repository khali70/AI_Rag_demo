"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ChangeEvent, FormEvent, useState } from "react";

import { deleteDocument, DocumentSummary, UploadResponse, fetchDocuments, uploadDocuments } from "@/lib/api";

export default function DocumentsPage() {
  const queryClient = useQueryClient();
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  const { data: documents = [], isLoading } = useQuery<DocumentSummary[], Error>({
    queryKey: ["documents"],
    queryFn: fetchDocuments,
  });

  const deleteMutation = useMutation<void, Error, string>({
    mutationFn: deleteDocument,
    onSuccess: () => {
      setStatusMessage("Document deleted.");
      setSelectedFiles([]);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (error) => setStatusMessage(error.message),
  });

  const uploadMutation = useMutation<UploadResponse, Error, File[]>({
    mutationFn: uploadDocuments,
    onSuccess: () => {
      setStatusMessage("Upload complete!");
      setSelectedFiles([]);
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (error: Error) => setStatusMessage(error.message),
  });

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    if (!event.target.files) return;
    setSelectedFiles(Array.from(event.target.files));
    setStatusMessage(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFiles.length) {
      setStatusMessage("Please select at least one .txt or .pdf file.");
      return;
    }
    uploadMutation.mutate(selectedFiles);
  }

  return (
    <div className="space-y-8">
      <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-xl">
        <h1 className="text-xl font-semibold text-white">Upload documents</h1>
        <p className="mt-2 text-sm text-slate-400">
          Supported formats: <code>.txt</code>, <code>.pdf</code>. Files are chunked, embedded, and indexed in Chroma.
        </p>
        <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
          <input
            type="file"
            multiple
            accept=".txt,.pdf"
            onChange={handleFileChange}
            className="w-full rounded border border-slate-700 bg-slate-900 px-4 py-3 text-sm"
          />
          <button
            type="submit"
            className="inline-flex items-center rounded bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-cyan-400 disabled:cursor-not-allowed disabled:bg-slate-700 disabled:text-slate-400"
            disabled={uploadMutation.isPending}
          >
            {uploadMutation.isPending ? "Uploading..." : "Upload & Process"}
          </button>
        </form>
        {statusMessage && <p className="mt-3 text-sm text-slate-300">{statusMessage}</p>}
      </section>

      <section>
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Documents</h2>
          {isLoading && <span className="text-sm text-slate-400">Loading...</span>}
        </div>
        {documents.length === 0 && !isLoading ? (
          <p className="mt-4 text-sm text-slate-400">No documents uploaded yet.</p>
        ) : (
          <div className="mt-4 overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60">
            <table className="min-w-full divide-y divide-slate-800 text-sm">
              <thead className="bg-slate-900 text-slate-400">
                <tr>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Chunks</th>
                  <th className="px-4 py-3 text-left">Embeddings</th>
                  <th className="px-4 py-3 text-left">Uploaded</th>
                  <th className="px-4 py-3 text-left">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {documents.map((doc) => (
                  <tr key={doc.id}>
                    <td className="px-4 py-3 font-medium text-white">{doc.filename}</td>
                    <td className="px-4 py-3">{doc.chunk_count}</td>
                    <td className="px-4 py-3">{doc.embedding_count}</td>
                    <td className="px-4 py-3 text-slate-400">
                      {new Date(doc.created_at).toLocaleString(undefined, {
                        hour12: false,
                      })}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => {
                          if (confirm(`Delete "${doc.filename}"? This removes embeddings and metadata.`)) {
                            deleteMutation.mutate(doc.id);
                          }
                        }}
                        className="text-xs font-semibold text-rose-400 hover:text-rose-300"
                        disabled={deleteMutation.isPending}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
