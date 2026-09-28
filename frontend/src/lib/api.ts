/**
 * API client for the VeriClaim backend.
 */

import type {
  AnalysisResponse,
  CitationDetail,
  DocumentStatistics,
  DocumentSummary,
  ProcessingStatus,
  VerificationResult,
} from "../types/api";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${path}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new ApiError(res.status, detail);
  }

  return res.json();
}

// ─── Documents ───

export async function uploadDocument(file: File): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return request<AnalysisResponse>("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  return request<DocumentSummary[]>("/documents");
}

export async function getDocumentStatus(
  documentId: string,
): Promise<ProcessingStatus> {
  return request<ProcessingStatus>(`/documents/${documentId}/status`);
}

export async function getDocumentResults(
  documentId: string,
): Promise<VerificationResult[]> {
  return request<VerificationResult[]>(`/documents/${documentId}/results`);
}

export async function getDocumentStatistics(
  documentId: string,
): Promise<DocumentStatistics> {
  return request<DocumentStatistics>(`/documents/${documentId}/statistics`);
}

// ─── Claims ───

export async function listClaims(params?: {
  document_id?: string;
  verdict?: string;
  claim_type?: string;
  section?: string;
  min_confidence?: number;
  max_confidence?: number;
  has_warnings?: boolean;
}): Promise<(VerificationResult & { document_id: string })[]> {
  const searchParams = new URLSearchParams();
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value));
      }
    }
  }
  const query = searchParams.toString();
  return request(`/claims${query ? `?${query}` : ""}`);
}

export async function getClaimDetail(
  claimId: string,
): Promise<VerificationResult & { document_id: string }> {
  return request(`/claims/${claimId}`);
}

export async function getClaimEvidence(claimId: string) {
  return request<{
    claim_id: string;
    claim_text: string;
    evidence: VerificationResult["evidence"];
    semantic_similarity: number | null;
    nli_result: VerificationResult["nli_result"];
    numerical_result: VerificationResult["numerical_result"];
  }>(`/claims/${claimId}/evidence`);
}

// ─── Citations ───

export async function listCitations(
  documentId: string,
): Promise<CitationDetail[]> {
  return request<CitationDetail[]>(
    `/citations?document_id=${documentId}`,
  );
}

// ─── System ───

export async function healthCheck(): Promise<{
  status: string;
  message: string;
  version: string;
}> {
  return request("/health");
}
