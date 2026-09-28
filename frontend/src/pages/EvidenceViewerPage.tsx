/**
 * Evidence Viewer: side-by-side claim vs. evidence comparison.
 */

import {
  AlertTriangle,
  BookOpen,
  CheckCircle,
  FileText,
  HelpCircle,
  XCircle,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { AnalysisResponse } from "../types/api";

interface EvidenceViewerPageProps {
  analysisData: AnalysisResponse | null;
}

const verdictIcons: Record<string, typeof CheckCircle> = {
  SUPPORTED: CheckCircle,
  "PARTIALLY SUPPORTED": AlertTriangle,
  CONTRADICTED: XCircle,
  "INSUFFICIENT EVIDENCE": HelpCircle,
};

const verdictBg: Record<string, string> = {
  SUPPORTED: "border-emerald-500",
  "PARTIALLY SUPPORTED": "border-amber-500",
  CONTRADICTED: "border-red-500",
  "INSUFFICIENT EVIDENCE": "border-slate-400",
};

export default function EvidenceViewerPage({ analysisData }: EvidenceViewerPageProps) {
  const navigate = useNavigate();
  const results = analysisData?.results || [];
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!analysisData || results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <BookOpen className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          No Evidence to Display
        </h2>
        <p className="text-slate-500 dark:text-slate-400 mb-4">Analyze a paper first.</p>
        <button
          onClick={() => navigate("/analyze")}
          className="text-sm text-blue-500 hover:text-blue-600 font-medium"
        >
          Analyze a Paper
        </button>
      </div>
    );
  }

  const selected = results[selectedIdx];
  const VerdictIcon = verdictIcons[selected.verdict] || HelpCircle;
  const borderColor = verdictBg[selected.verdict] || verdictBg["INSUFFICIENT EVIDENCE"];

  return (
    <div className="flex flex-col h-full animate-fade-in">
      {/* Header */}
      <div className="px-4 sm:px-6 py-4 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-theme">
        <div className="flex items-center justify-between gap-4 max-w-[1400px] mx-auto">
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-white">
              Evidence Viewer
            </h1>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              Side-by-side comparison · Claim {selectedIdx + 1} of {results.length}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedIdx(Math.max(0, selectedIdx - 1))}
              disabled={selectedIdx === 0}
              className="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              ← Prev
            </button>
            <button
              onClick={() => setSelectedIdx(Math.min(results.length - 1, selectedIdx + 1))}
              disabled={selectedIdx === results.length - 1}
              className="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* Side-by-side */}
      <div className="flex-1 overflow-auto p-4 sm:p-6">
        <div className="max-w-[1400px] mx-auto grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* Left: Claim */}
          <div className={`rounded-xl border-l-4 ${borderColor} bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden transition-theme`}>
            <div className="px-5 py-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">Claim</h3>
              </div>
            </div>
            <div className="p-5">
              <blockquote className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed mb-4">
                "{selected.claim_text}"
              </blockquote>

              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <VerdictIcon className="w-4 h-4" />
                  <span className="text-sm font-semibold">{selected.verdict}</span>
                  <span className="text-xs text-slate-400">
                    ({(selected.confidence * 100).toFixed(0)}% confidence)
                  </span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-blue-500 bg-blue-50 dark:bg-blue-900/20 px-2 py-0.5 rounded">
                    {selected.claim_type}
                  </span>
                  {selected.linked_citations.map((c) => (
                    <span key={c} className="text-[10px] font-medium text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">
                      {c}
                    </span>
                  ))}
                </div>

                {selected.warnings.length > 0 && (
                  <div className="mt-3 space-y-1">
                    {selected.warnings.map((w, i) => (
                      <p key={i} className="text-xs text-amber-600 dark:text-amber-400 flex items-start gap-1.5">
                        <AlertTriangle className="w-3 h-3 shrink-0 mt-0.5" />
                        {w}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right: Evidence */}
          <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden transition-theme">
            <div className="px-5 py-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-slate-400" />
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                  Retrieved Evidence
                </h3>
              </div>
            </div>
            <div className="p-5 space-y-4">
              {selected.evidence.length > 0 ? (
                selected.evidence.map((ev, i) => (
                  <div key={i} className="border-l-2 border-blue-200 dark:border-blue-800 pl-4 py-2">
                    <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed">
                      "{ev.text}"
                    </p>
                    <div className="flex items-center gap-3 mt-2 text-xs text-slate-400 dark:text-slate-500 flex-wrap">
                      <span className="font-mono">
                        Similarity: {ev.score.toFixed(3)}
                      </span>
                      {ev.page_number > 0 && (
                        <span>Page {ev.page_number}</span>
                      )}
                      {ev.section && <span>§ {ev.section}</span>}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-400 italic">No evidence passages retrieved.</p>
              )}

              {/* NLI Summary */}
              {selected.nli_result && (
                <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
                    NLI Breakdown
                  </p>
                  <div className="flex gap-4 text-xs text-slate-500 dark:text-slate-400">
                    <span>
                      Entail: <strong className="text-emerald-500">{(selected.nli_result.entailment * 100).toFixed(1)}%</strong>
                    </span>
                    <span>
                      Neutral: <strong>{(selected.nli_result.neutral * 100).toFixed(1)}%</strong>
                    </span>
                    <span>
                      Contra: <strong className="text-red-500">{(selected.nli_result.contradiction * 100).toFixed(1)}%</strong>
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Explanation */}
        <div className="max-w-[1400px] mx-auto mt-4">
          <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 transition-theme">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-2">
              Reasoning
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {selected.explanation}
            </p>
          </div>
        </div>
      </div>

      {/* Claim selector strip */}
      <div className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-4 py-3 overflow-x-auto transition-theme">
        <div className="flex gap-2 max-w-[1400px] mx-auto">
          {results.map((r, i) => {
            const Icon = verdictIcons[r.verdict] || HelpCircle;
            return (
              <button
                key={r.claim_id}
                onClick={() => setSelectedIdx(i)}
                className={`shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  i === selectedIdx
                    ? "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800"
                    : "text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 border border-transparent"
                }`}
              >
                <Icon className="w-3 h-3" />
                #{i + 1}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
