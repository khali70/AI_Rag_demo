export type DocumentSummary = {
  id: string;
  filename: string;
  content_type: string;
  chunk_count: number;
  embedding_count: number;
  created_at: string;
};

export type UploadResponse = {
  documents: DocumentSummary[];
  count: number;
};

export type SourceInfo = {
  chunk_id: string;
  document_id: string;
  document_name: string;
  chunk_index: number;
  score?: number | null;
  snippet: string;
};

export type AskResponse = {
  answer: string;
  sources: SourceInfo[];
};

const DEFAULT_PUBLIC_BASE_URL = "http://localhost:8000/api";
const DEFAULT_INTERNAL_BASE_URL = "http://backend:8000/api";

const getApiBase = () => {
  if (typeof window === "undefined") {
    return process.env.API_INTERNAL_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_INTERNAL_BASE_URL;
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_PUBLIC_BASE_URL;
};

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || "Request failed");
  }
  return res.json() as Promise<T>;
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const res = await fetch(`${getApiBase()}/docs`, { cache: "no-store" });
  const data = await handleResponse<{ documents: DocumentSummary[] }>(res);
  return data.documents;
}

export async function uploadDocuments(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${getApiBase()}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<UploadResponse>(res);
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${getApiBase()}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return handleResponse<AskResponse>(res);
}
