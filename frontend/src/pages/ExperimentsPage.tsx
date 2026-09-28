/**
 * Experiments page: placeholder for model comparison and ablation studies.
 */

import { FlaskConical, Layers, SlidersHorizontal } from "lucide-react";

export default function ExperimentsPage() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          Experiments
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Model comparison, ablation studies, and evaluation metrics.
        </p>
      </div>

      <div className="grid gap-4">
        {/* Model Comparison */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/20 flex items-center justify-center">
              <SlidersHorizontal className="w-5 h-5 text-blue-500" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Model Comparison
              </h2>
              <p className="text-xs text-slate-400 dark:text-slate-500">
                Compare precision, recall, F1, and latency across models.
              </p>
            </div>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Currently using: <span className="font-mono text-xs text-blue-500">all-MiniLM-L6-v2</span> (embeddings),{" "}
            <span className="font-mono text-xs text-blue-500">cross-encoder/nli-deberta-v3-small</span> (NLI),{" "}
            <span className="font-mono text-xs text-blue-500">distilbart-mnli-12-1</span> (claim detection).
          </p>
          <p className="mt-3 text-xs text-slate-400 dark:text-slate-500 italic">
            Full model comparison interface will be available in a future update.
          </p>
        </div>

        {/* Ablation Studies */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-violet-50 dark:bg-violet-900/20 flex items-center justify-center">
              <Layers className="w-5 h-5 text-violet-500" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Ablation Studies
              </h2>
              <p className="text-xs text-slate-400 dark:text-slate-500">
                Test pipeline component contributions.
              </p>
            </div>
          </div>
          <div className="space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800">A</span>
              Semantic similarity only
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800">B</span>
              Similarity + NLI
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800">C</span>
              Similarity + NLI + Numerical Consistency
            </div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">D</span>
              Full VeriClaim Pipeline
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-400 dark:text-slate-500 italic">
            Run experiments from the backend: <code className="font-mono">python backend/experiments/evaluator.py</code>
          </p>
        </div>

        {/* Current Pipeline Config */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 flex items-center justify-center">
              <FlaskConical className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                Current Configuration
              </h2>
              <p className="text-xs text-slate-400 dark:text-slate-500">
                Active pipeline settings.
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-3">
            {[
              { key: "Embedding Model", value: "all-MiniLM-L6-v2" },
              { key: "NLI Model", value: "nli-deberta-v3-small" },
              { key: "Claim Detector", value: "distilbart-mnli-12-1" },
              { key: "Top-K Retrieval", value: "3" },
              { key: "Embedding Dim", value: "384" },
              { key: "FAISS Index", value: "IndexFlatIP" },
            ].map((item) => (
              <div key={item.key} className="flex justify-between items-center text-sm py-1.5 px-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
                <span className="text-slate-500 dark:text-slate-400">{item.key}</span>
                <span className="font-mono text-xs text-slate-700 dark:text-slate-300">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
