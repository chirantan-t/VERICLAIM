/**
 * Citation Explorer: displays all citations with usage statistics.
 */

import {
  AlertTriangle,
  CheckCircle,
  HelpCircle,
  Quote,
  XCircle,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { AnalysisResponse, VerificationResult } from "../types/api";

interface CitationExplorerPageProps {
  analysisData: AnalysisResponse | null;
}

interface CitationData {
  ref_id: string;
  raw_text: string;
  authors?: string[];
  title?: string;
  year?: number;
  claims: VerificationResult[];
  supported: number;
  partial: number;
  contradicted: number;
  insufficient: number;
}

export default function CitationExplorerPage({ analysisData }: CitationExplorerPageProps) {
  const navigate = useNavigate();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const citations = useMemo<CitationData[]>(() => {
    if (!analysisData) return [];

    return analysisData.document.references.map((ref) => {
      const relatedClaims = analysisData.results.filter((r) =>
        r.linked_citations.includes(ref.ref_id),
      );

      return {
        ref_id: ref.ref_id,
        raw_text: ref.raw_text,
        authors: ref.authors ?? undefined,
        title: ref.title ?? undefined,
        year: ref.year ?? undefined,
        claims: relatedClaims,
        supported: relatedClaims.filter((c) => c.verdict === "SUPPORTED").length,
        partial: relatedClaims.filter((c) => c.verdict === "PARTIALLY SUPPORTED").length,
        contradicted: relatedClaims.filter((c) => c.verdict === "CONTRADICTED").length,
        insufficient: relatedClaims.filter((c) => c.verdict === "INSUFFICIENT EVIDENCE").length,
      };
    });
  }, [analysisData]);

  if (!analysisData) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <Quote className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          No Citations to Explore
        </h2>
        <p className="text-slate-500 dark:text-slate-400">Analyze a paper first.</p>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-[1200px] mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          Citation Explorer
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          {citations.length} references found · {citations.filter((c) => c.claims.length > 0).length} with verified claims
        </p>
      </div>

      <div className="space-y-3">
        {citations.map((cit) => (
          <div
            key={cit.ref_id}
            className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 overflow-hidden transition-theme"
          >
            {/* Citation header */}
            <div
              className="px-5 py-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
              onClick={() => setExpandedId(expandedId === cit.ref_id ? null : cit.ref_id)}
            >
              <div className="flex items-start gap-3">
                <span className="shrink-0 text-xs font-bold text-blue-500 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded mt-0.5">
                  {cit.ref_id}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-800 dark:text-slate-200 line-clamp-2">
                    {cit.title || cit.raw_text}
                  </p>
                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    {cit.authors && cit.authors.length > 0 && (
                      <span className="text-xs text-slate-400 dark:text-slate-500">
                        {cit.authors.slice(0, 3).join(", ")}
                        {cit.authors.length > 3 && " et al."}
                      </span>
                    )}
                    {cit.year && (
                      <span className="text-xs text-slate-400 dark:text-slate-500">
                        {cit.year}
                      </span>
                    )}
                  </div>
                </div>

                {/* Usage stats */}
                <div className="shrink-0 flex items-center gap-2 flex-wrap justify-end">
                  <span className="text-xs font-medium text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                    {cit.claims.length} claim{cit.claims.length !== 1 ? "s" : ""}
                  </span>
                  {cit.supported > 0 && (
                    <span className="flex items-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
                      <CheckCircle className="w-3 h-3" /> {cit.supported}
                    </span>
                  )}
                  {cit.partial > 0 && (
                    <span className="flex items-center gap-1 text-xs text-amber-500">
                      <AlertTriangle className="w-3 h-3" /> {cit.partial}
                    </span>
                  )}
                  {cit.contradicted > 0 && (
                    <span className="flex items-center gap-1 text-xs text-red-500">
                      <XCircle className="w-3 h-3" /> {cit.contradicted}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Expanded: related claims */}
            {expandedId === cit.ref_id && cit.claims.length > 0 && (
              <div className="border-t border-slate-100 dark:border-slate-800 divide-y divide-slate-50 dark:divide-slate-800 animate-scale-in">
                <div className="px-5 py-2 bg-slate-50 dark:bg-slate-800/50">
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                    Claims citing {cit.ref_id}
                  </span>
                </div>
                {cit.claims.map((claim) => {
                  const Icon =
                    claim.verdict === "SUPPORTED" ? CheckCircle :
                    claim.verdict === "PARTIALLY SUPPORTED" ? AlertTriangle :
                    claim.verdict === "CONTRADICTED" ? XCircle : HelpCircle;
                  return (
                    <div
                      key={claim.claim_id}
                      className="px-5 py-3 flex items-start gap-3 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                      onClick={() => navigate(`/claims/${claim.claim_id}`)}
                    >
                      <Icon className="w-4 h-4 shrink-0 mt-0.5 text-slate-400" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2">
                          {claim.claim_text}
                        </p>
                      </div>
                      <span className="shrink-0 text-xs text-slate-400">
                        {(claim.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  );
                })}
              </div>
            )}

            {expandedId === cit.ref_id && cit.claims.length === 0 && (
              <div className="border-t border-slate-100 dark:border-slate-800 px-5 py-4 text-sm text-slate-400 italic animate-scale-in">
                No verified claims cite this reference.
              </div>
            )}
          </div>
        ))}

        {citations.length === 0 && (
          <div className="text-center py-12 text-slate-400 dark:text-slate-500 text-sm">
            No references found in this document.
          </div>
        )}
      </div>
    </div>
  );
}
