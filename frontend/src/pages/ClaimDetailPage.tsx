/**
 * Claim Detail page: full verification analysis for a single claim.
 */

import {
  AlertTriangle,
  ArrowLeft,
  BookOpen,
  CheckCircle,
  FileText,
  Hash,
  HelpCircle,
  Scale,
  XCircle,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import type { AnalysisResponse } from "../types/api";

interface ClaimDetailPageProps {
  analysisData: AnalysisResponse | null;
}

const verdictConfig: Record<string, { icon: typeof CheckCircle; class: string }> = {
  SUPPORTED: { icon: CheckCircle, class: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/40" },
  "PARTIALLY_SUPPORTED": { icon: AlertTriangle, class: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/40" },
  CONTRADICTED: { icon: XCircle, class: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/40" },
  "INSUFFICIENT_EVIDENCE": { icon: HelpCircle, class: "text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-800 border-slate-200 dark:border-slate-700" },
  "SOURCE_UNAVAILABLE": { icon: AlertTriangle, class: "text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800/40" },
};

export default function ClaimDetailPage({ analysisData }: ClaimDetailPageProps) {
  const { claimId } = useParams<{ claimId: string }>();
  const navigate = useNavigate();

  const claim = analysisData?.results.find((r) => r.claim_id === claimId);

  if (!claim) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <HelpCircle className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">Claim Not Found</h2>
        <button onClick={() => navigate("/claims")} className="text-sm text-blue-500 hover:text-blue-600">
          Back to Claims
        </button>
      </div>
    );
  }

  const config = verdictConfig[claim.verdict] || verdictConfig["INSUFFICIENT_EVIDENCE"];
  const VerdictIcon = config.icon;
  const claimIndex = analysisData!.results.indexOf(claim) + 1;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      {/* Back */}
      <button
        onClick={() => navigate("/claims")}
        className="inline-flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Claims
      </button>

      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-3 flex-wrap">
          <span className="text-xs font-mono text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
            CLAIM #{claimIndex}
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-blue-500 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
            {claim.claim_type}
          </span>
          {claim.section && (
            <span className="text-xs text-slate-400 dark:text-slate-500">
              § {claim.section}
            </span>
          )}
          {claim.page_number && (
            <span className="text-xs text-slate-400 dark:text-slate-500">
              p. {claim.page_number}
            </span>
          )}
        </div>

        <blockquote className="text-lg sm:text-xl font-medium text-slate-900 dark:text-white leading-relaxed border-l-4 border-blue-500 pl-4 py-1">
          "{claim.claim_text}"
        </blockquote>

        {claim.linked_citations.length > 0 && (
          <div className="flex items-center gap-2 mt-3">
            <span className="text-xs font-medium text-slate-400 dark:text-slate-500">Citations:</span>
            {claim.linked_citations.map((c) => (
              <span key={c} className="text-xs font-semibold text-blue-500 bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded">
                {c}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Verdict card */}
      <div className={`p-5 rounded-xl border ${config.class} mb-6`}>
        <div className="flex items-center gap-3">
          <VerdictIcon className="w-6 h-6" />
          <div>
            <p className="text-lg font-bold">{claim.verdict}</p>
            <p className="text-sm opacity-80">
              Confidence: {(claim.confidence * 100).toFixed(1)}%
            </p>
          </div>
        </div>
      </div>

      {/* Warnings */}
      {claim.warnings.length > 0 && (
        <div className="mb-6 space-y-2">
          {claim.warnings.map((w, i) => (
            <div key={i} className="flex items-start gap-2 p-3 rounded-lg bg-amber-50 dark:bg-amber-900/10 border border-amber-100 dark:border-amber-800/30 text-sm text-amber-700 dark:text-amber-400">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{w}</span>
            </div>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Retrieved Evidence */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden transition-theme">
          <div className="px-5 py-3 border-b border-slate-100 dark:border-slate-800 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-slate-400" />
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
              Retrieved Evidence
            </h3>
          </div>
          <div className="p-5 space-y-4">
            {claim.evidence.length > 0 ? (
              claim.evidence.map((ev, i) => (
                <div key={i} className="border-l-2 border-slate-200 dark:border-slate-700 pl-4">
                  <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
                    "{ev.text}"
                  </p>
                  <div className="flex items-center gap-3 mt-2 text-xs text-slate-400 dark:text-slate-500">
                    <span>Score: {ev.score.toFixed(3)}</span>
                    {ev.page_number > 0 && <span>Page {ev.page_number}</span>}
                    {ev.section && <span>§ {ev.section}</span>}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-400 italic">No evidence retrieved.</p>
            )}
          </div>
        </div>

        {/* Analysis Details */}
        <div className="space-y-4">
          {/* Semantic Similarity */}
          {claim.semantic_similarity !== null && claim.semantic_similarity !== undefined && (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 transition-theme">
              <div className="flex items-center gap-2 mb-3">
                <Scale className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Semantic Similarity
                </h3>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-3 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-blue-500 transition-all"
                    style={{ width: `${claim.semantic_similarity * 100}%` }}
                  />
                </div>
                <span className="text-lg font-bold text-slate-900 dark:text-white">
                  {claim.semantic_similarity.toFixed(3)}
                </span>
              </div>
            </div>
          )}

          {/* NLI Result */}
          {claim.nli_result && (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 transition-theme">
              <div className="flex items-center gap-2 mb-3">
                <FileText className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  NLI Analysis
                </h3>
              </div>
              <div className="space-y-3">
                {[
                  { label: "Entailment", value: claim.nli_result.entailment, color: "#10b981" },
                  { label: "Neutral", value: claim.nli_result.neutral, color: "#64748b" },
                  { label: "Contradiction", value: claim.nli_result.contradiction, color: "#ef4444" },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-3">
                    <span className="text-xs font-medium text-slate-500 dark:text-slate-400 w-24">
                      {item.label}
                    </span>
                    <div className="flex-1 h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{ width: `${item.value * 100}%`, backgroundColor: item.color }}
                      />
                    </div>
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400 w-12 text-right">
                      {(item.value * 100).toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Numerical Analysis */}
          {claim.numerical_result && claim.numerical_result.status !== "NO_NUMBERS_IN_CLAIM" && (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 transition-theme">
              <div className="flex items-center gap-2 mb-3">
                <Hash className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Numerical Analysis
                </h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-slate-400 dark:text-slate-500">Status:</span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
                    claim.numerical_result.status === "CONSISTENT"
                      ? "text-emerald-600 bg-emerald-50 dark:text-emerald-400 dark:bg-emerald-900/20"
                      : claim.numerical_result.status === "APPROXIMATE"
                        ? "text-amber-600 bg-amber-50 dark:text-amber-400 dark:bg-amber-900/20"
                        : "text-red-600 bg-red-50 dark:text-red-400 dark:bg-red-900/20"
                  }`}>
                    {claim.numerical_result.status}
                  </span>
                </div>
                {claim.numerical_result.claim_numbers.length > 0 && (
                  <p className="text-slate-600 dark:text-slate-400">
                    <span className="font-medium">Claim:</span>{" "}
                    {claim.numerical_result.claim_numbers.join(", ")}
                  </p>
                )}
                {claim.numerical_result.evidence_numbers.length > 0 && (
                  <p className="text-slate-600 dark:text-slate-400">
                    <span className="font-medium">Evidence:</span>{" "}
                    {claim.numerical_result.evidence_numbers.join(", ")}
                  </p>
                )}
                {claim.numerical_result.missing_numbers.length > 0 && (
                  <p className="text-red-600 dark:text-red-400">
                    <span className="font-medium">Missing:</span>{" "}
                    {claim.numerical_result.missing_numbers.join(", ")}
                  </p>
                )}
                {claim.numerical_result.message && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-2 italic">
                    {claim.numerical_result.message}
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Final Reasoning */}
      <div className="mt-6 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 transition-theme">
        <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-3">
          Verification Reasoning
        </h3>
        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed bg-slate-50 dark:bg-slate-800/60 p-4 rounded-lg">
          {claim.explanation}
        </p>
      </div>
    </div>
  );
}
