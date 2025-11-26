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

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type TitleResponse = {
  title: string;
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
  const res = await fetch(`${getApiBase()}/docs`, {
    cache: "no-store",
    headers: buildAuthHeaders(),
  });
  const data = await handleResponse<{ documents: DocumentSummary[] }>(res);
  return data.documents;
}

export async function uploadDocuments(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${getApiBase()}/upload`, {
    method: "POST",
    headers: buildAuthHeaders(),
    body: formData,
  });

  return handleResponse<UploadResponse>(res);
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await fetch(`${getApiBase()}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(),
    },
    body: JSON.stringify({ question }),
  });
  return handleResponse<AskResponse>(res);
}

export async function generateSessionTitle(context: string): Promise<string> {
  const res = await fetch(`${getApiBase()}/ask/title`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...buildAuthHeaders(),
    },
    body: JSON.stringify({ context }),
  });
  const data = await handleResponse<TitleResponse>(res);
  return data.title;
}

function buildAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("nixai_token");
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

export async function signup(email: string, password: string): Promise<void> {
  const res = await fetch(`${getApiBase()}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  await handleResponse(res);
}

export async function login(email: string, password: string): Promise<string> {
  const res = await fetch(`${getApiBase()}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await handleResponse<TokenResponse>(res);
  if (typeof window !== "undefined") {
    window.localStorage.setItem("nixai_token", data.access_token);
  }
  return data.access_token;
}

export function logout() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("nixai_token");
}
