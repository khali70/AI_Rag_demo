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
  refresh_token: string;
  expires_in: number;
  refresh_expires_in: number;
  token_type: string;
};

export type TitleResponse = {
  title: string;
};

const DEFAULT_PUBLIC_BASE_URL = "http://localhost:8000/api";
const DEFAULT_INTERNAL_BASE_URL = "http://backend:8000/api";

const getApiBase = () => {
  if (typeof window === "undefined") {
    return (
      process.env.API_INTERNAL_BASE_URL ??
      process.env.NEXT_PUBLIC_API_BASE_URL ??
      DEFAULT_INTERNAL_BASE_URL
    );
  }
  return process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_PUBLIC_BASE_URL;
};

function buildAuthHeaders(): HeadersInit {
  if (typeof window === "undefined") return {};
  const token = window.localStorage.getItem("nixai_token");
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

function setTokens(accessToken: string, refreshToken: string) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("nixai_token", accessToken);
  window.localStorage.setItem("nixai_refresh_token", refreshToken);
}

function clearTokens() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("nixai_token");
  window.localStorage.removeItem("nixai_refresh_token");
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const message = await res.text();
    throw new Error(message || "Request failed");
  }
  return res.json() as Promise<T>;
}

async function authFetch(
  input: RequestInfo,
  init: RequestInit = {},
  attemptRefresh = true,
): Promise<Response> {
  const headers = {
    ...(init.headers ?? {}),
    ...buildAuthHeaders(),
  };
  const response = await fetch(input, { ...init, headers });

  if (response.status === 401 && attemptRefresh) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return authFetch(input, init, false);
    }
    logout();
    if (typeof window !== "undefined") {
      window.location.href = "/auth/login";
    }
  }

  return response;
}

export async function refreshAccessToken(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  const refreshToken = window.localStorage.getItem("nixai_refresh_token");
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${getApiBase()}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    const data = await handleResponse<TokenResponse>(res);
    setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    clearTokens();
    return false;
  }
}

export async function fetchDocuments(): Promise<DocumentSummary[]> {
  const res = await authFetch(`${getApiBase()}/docs`, {
    cache: "no-store",
  });
  const data = await handleResponse<{ documents: DocumentSummary[] }>(res);
  return data.documents;
}

export async function uploadDocuments(files: File[]): Promise<UploadResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await authFetch(`${getApiBase()}/upload`, {
    method: "POST",
    body: formData,
  });

  return handleResponse<UploadResponse>(res);
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await authFetch(`${getApiBase()}/docs/${documentId}`, {
    method: "DELETE",
  });
  await handleResponse(res);
}

export async function askQuestion(question: string): Promise<AskResponse> {
  const res = await authFetch(`${getApiBase()}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  return handleResponse<AskResponse>(res);
}

export async function generateSessionTitle(context: string): Promise<string> {
  const res = await authFetch(`${getApiBase()}/ask/title`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ context }),
  });
  const data = await handleResponse<TitleResponse>(res);
  return data.title;
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
  setTokens(data.access_token, data.refresh_token);
  return data.access_token;
}

export function logout() {
  clearTokens();
}

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("nixai_token");
}
