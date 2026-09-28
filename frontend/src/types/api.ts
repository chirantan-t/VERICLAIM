/**
 * API types matching backend Pydantic schemas.
 */

export type ClaimType =
  | "factual"
  | "numerical"
  | "comparative"
  | "causal"
  | "methodological"
  | "statistical"
  | "conclusion";

export type VerdictType =
  | "SUPPORTED"
  | "PARTIALLY_SUPPORTED"
  | "CONTRADICTED"
  | "INSUFFICIENT_EVIDENCE"
  | "SOURCE_UNAVAILABLE"
  | "RETRIEVAL_FAILED";

export type ProcessingStageType =
  | "queued"
  | "parsing"
  | "extracting_citations"
  | "detecting_claims"
  | "linking_citations"
  | "retrieving_evidence"
  | "semantic_analysis"
  | "nli_verification"
  | "numerical_checking"
  | "generating_report"
  | "complete"
  | "error";

export interface Sentence {
  sentence_id: string;
  text: string;
  page_number: number;
  section?: string;
  citation_markers: string[];
}

export interface Paragraph {
  paragraph_id: string;
  text: string;
  page_number: number;
  sentences: Sentence[];
}

export interface Section {
  title: string;
  paragraphs: Paragraph[];
}

export interface Reference {
  ref_id: string;
  raw_text: string;
  title?: string;
  authors?: string[];
  year?: number;
  journal?: string;
  doi?: string;
  url?: string;
  source_id?: string;
  retrieval_status: string;
}

export interface DocumentMetadata {
  title?: string;
  authors?: string[];
  abstract?: string;
  pages?: number;
  file_size?: number;
  filename?: string;
}

export interface ExtractedClaim {
  claim_id: string;
  text: string;
  source_sentence_id: string;
  section?: string;
  page_number?: number;
  linked_citations: string[];
  claim_type: ClaimType;
}

export interface ParsedDocument {
  document_id: string;
  metadata: DocumentMetadata;
  sections: Section[];
  references: Reference[];
  claims: ExtractedClaim[];
}

export interface Evidence {
  source_id: string;
  document_title?: string;
  source_type: string;
  sentence_id: string;
  text: string;
  score: number;
  page_number: number;
  section?: string;
  source_url?: string;
}

export interface NLIResult {
  entailment: number;
  neutral: number;
  contradiction: number;
  predicted_label: string;
}

export interface NumericalResult {
  status: string;
  claim_numbers: string[];
  evidence_numbers: string[];
  missing_numbers: string[];
  approximate_matches: { claim: string; evidence: string }[];
  matched_numbers: string[];
  message?: string;
}

export interface VerificationResult {
  claim_id: string;
  claim_text: string;
  claim_type: ClaimType;
  section?: string;
  page_number?: number;
  linked_citations: string[];
  verdict: VerdictType;
  confidence: number;
  explanation: string;
  warnings: string[];
  evidence: Evidence[];
  nli_result?: NLIResult;
  numerical_result?: NumericalResult;
  semantic_similarity?: number;
}

export interface DocumentStatistics {
  total_claims: number;
  total_citations: number;
  total_evidence: number;
  resolved_citations: number;
  unresolved_citations: number;
  claims_supported: number;
  claims_partially_supported: number;
  claims_contradicted: number;
  claims_insufficient: number;
  average_confidence: number;
  verdict_distribution: Record<string, number>;
  claim_type_distribution: Record<string, number>;
  section_distribution: Record<string, number>;
  numerical_discrepancies: number;
  low_confidence_claims: number;
}

export interface ProcessingStatus {
  document_id: string;
  stage: ProcessingStageType;
  progress: number;
  message: string;
  started_at?: string;
  completed_at?: string;
  error?: string;
}

export interface AnalysisResponse {
  document: ParsedDocument;
  results: VerificationResult[];
  statistics: DocumentStatistics;
  processing_status?: ProcessingStatus;
}

export interface DocumentSummary {
  document_id: string;
  title?: string;
  filename?: string;
  file_size?: number;
  pages?: number;
  status: string;
  total_claims: number;
  total_citations: number;
}

export interface CitationDetail {
  ref_id: string;
  raw_text: string;
  authors?: string[];
  title?: string;
  year?: number;
  venue?: string;
  claims_using: number;
  supported: number;
  partially_supported: number;
  contradicted: number;
  insufficient: number;
  claims: {
    claim_id: string;
    claim_text: string;
    verdict: VerdictType;
    confidence: number;
  }[];
}
