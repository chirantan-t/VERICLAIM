/**
 * Research Graph page: placeholder for knowledge graph visualization.
 */

import { Network } from "lucide-react";
import type { AnalysisResponse } from "../types/api";

interface ResearchGraphPageProps {
  analysisData: AnalysisResponse | null;
}

export default function ResearchGraphPage({ analysisData }: ResearchGraphPageProps) {
  if (!analysisData) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <Network className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          Research Graph
        </h2>
        <p className="text-slate-500 dark:text-slate-400">Analyze a paper to visualize the research graph.</p>
      </div>
    );
  }

  const { results, document: doc } = analysisData;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-5xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          Research Graph
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Relationship map between claims, evidence, and citations.
        </p>
      </div>

      {/* Graph placeholder */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 transition-theme text-center">
        <Network className="w-16 h-16 text-slate-300 dark:text-slate-600 mx-auto mb-4" />
        <h3 className="text-base font-semibold text-slate-700 dark:text-slate-300 mb-2">
          Interactive Graph Coming Soon
        </h3>
        <p className="text-sm text-slate-400 dark:text-slate-500 max-w-md mx-auto">
          This visualization will show the relationships between {results.length} claims,{" "}
          {doc.references.length} references, and their evidence passages as an interactive
          network graph.
        </p>
      </div>

      {/* Graph summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
        {[
          { label: "Claims (nodes)", value: results.length, color: "text-blue-500" },
          { label: "References (nodes)", value: doc.references.length, color: "text-violet-500" },
          {
            label: "Citation Links (edges)",
            value: results.reduce((sum, r) => sum + r.linked_citations.length, 0),
            color: "text-cyan-500",
          },
          {
            label: "Evidence Links (edges)",
            value: results.reduce((sum, r) => sum + r.evidence.length, 0),
            color: "text-emerald-500",
          },
        ].map((s) => (
          <div
            key={s.label}
            className="p-4 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 text-center transition-theme"
          >
            <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
