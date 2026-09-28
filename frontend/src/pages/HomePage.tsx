/**
 * Home / Landing page with hero section and pipeline explanation.
 */

import {
  ArrowRight,
  BookOpen,
  FileSearch,
  Link2,
  Scale,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import type { AnalysisResponse } from "../types/api";

interface HomePageProps {
  analysisData: AnalysisResponse | null;
}

const pipelineSteps = [
  { icon: FileSearch, label: "Extract Claims", desc: "Detect scientific claims using NLP" },
  { icon: Link2, label: "Link Citations", desc: "Connect claims to cited sources" },
  { icon: BookOpen, label: "Retrieve Evidence", desc: "Semantic search for relevant passages" },
  { icon: Scale, label: "Verify", desc: "NLI + numerical consistency + verdict" },
];

export default function HomePage({ analysisData }: HomePageProps) {
  const navigate = useNavigate();

  return (
    <div className="min-h-full flex flex-col">
      {/* Hero */}
      <section className="flex-1 flex items-center justify-center px-4 py-16 sm:py-24">
        <div className="max-w-3xl mx-auto text-center animate-fade-in">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-xs font-semibold mb-6 border border-blue-100 dark:border-blue-800/40">
            <Sparkles className="w-3.5 h-3.5" />
            Research-Grade NLP Verification
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-6 leading-[1.1]">
            VERI<span className="text-blue-500">CLAIM</span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 dark:text-slate-400 mb-10 max-w-2xl mx-auto leading-relaxed">
            Verify whether scientific claims are actually supported by their
            cited evidence — using semantic retrieval, natural language
            inference, and numerical consistency analysis.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button
              onClick={() => navigate("/analyze")}
              className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-lg shadow-blue-500/20 hover:shadow-blue-500/30 transition-all duration-200 active:scale-[0.98]"
            >
              <ShieldCheck className="w-4.5 h-4.5" />
              Analyze a Paper
            </button>
            {analysisData && (
              <button
                onClick={() => navigate("/dashboard")}
                className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-semibold text-sm hover:bg-slate-50 dark:hover:bg-slate-700 transition-all duration-200"
              >
                View Results
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Pipeline explanation */}
      <section className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 px-4 py-16 transition-theme">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-center text-sm font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-10">
            Verification Pipeline
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {pipelineSteps.map((step, i) => (
              <div
                key={step.label}
                className="relative flex flex-col items-center text-center p-6 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 animate-slide-up"
                style={{ animationDelay: `${i * 100}ms`, animationFillMode: "backwards" }}
              >
                {i < pipelineSteps.length - 1 && (
                  <div className="hidden lg:block absolute -right-3 top-1/2 -translate-y-1/2 z-10">
                    <ArrowRight className="w-4 h-4 text-slate-300 dark:text-slate-600" />
                  </div>
                )}
                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center mb-3">
                  <step.icon className="w-5 h-5 text-blue-500" />
                </div>
                <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
                  {step.label}
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Summary stats from real data */}
      {analysisData && (
        <section className="border-t border-slate-200 dark:border-slate-800 px-4 py-12 transition-theme">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-center text-sm font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-8">
              Latest Analysis
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Claims Analyzed", value: analysisData.statistics.total_claims },
                { label: "Citations Found", value: analysisData.statistics.total_citations },
                { label: "Evidence Retrieved", value: analysisData.statistics.total_evidence },
                {
                  label: "Avg. Confidence",
                  value: `${(analysisData.statistics.average_confidence * 100).toFixed(0)}%`,
                },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="flex flex-col items-center p-4 rounded-xl bg-white dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50"
                >
                  <span className="text-2xl font-bold text-slate-900 dark:text-white">
                    {stat.value}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    {stat.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
