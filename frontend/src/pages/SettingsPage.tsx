/**
 * Settings page: theme, model configuration, and system info.
 */

import { Moon, Sun } from "lucide-react";

interface SettingsPageProps {
  isDark: boolean;
  onThemeToggle: () => void;
}

export default function SettingsPage({ isDark, onThemeToggle }: SettingsPageProps) {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-3xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
          Settings
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Application preferences and configuration.
        </p>
      </div>

      <div className="space-y-6">
        {/* Appearance */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            Appearance
          </h2>
          <div className="flex gap-3">
            <button
              onClick={() => !isDark || onThemeToggle()}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                !isDark
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              }`}
            >
              <Sun className={`w-6 h-6 ${!isDark ? "text-blue-500" : "text-slate-400"}`} />
              <span className={`text-sm font-medium ${!isDark ? "text-blue-600" : "text-slate-500 dark:text-slate-400"}`}>
                Light
              </span>
            </button>
            <button
              onClick={() => isDark || onThemeToggle()}
              className={`flex-1 flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${
                isDark
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600"
              }`}
            >
              <Moon className={`w-6 h-6 ${isDark ? "text-blue-500" : "text-slate-400"}`} />
              <span className={`text-sm font-medium ${isDark ? "text-blue-400" : "text-slate-500 dark:text-slate-400"}`}>
                Dark
              </span>
            </button>
          </div>
        </div>

        {/* Model Configuration (read-only) */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
            Model Configuration
          </h2>
          <div className="space-y-3">
            {[
              {
                label: "Embedding Model",
                value: "all-MiniLM-L6-v2",
                desc: "384-dim sentence embeddings for semantic retrieval",
              },
              {
                label: "NLI Model",
                value: "cross-encoder/nli-deberta-v3-small",
                desc: "Natural Language Inference for claim verification",
              },
              {
                label: "Claim Detector",
                value: "valhalla/distilbart-mnli-12-1",
                desc: "Zero-shot classification for claim detection",
              },
            ].map((model) => (
              <div
                key={model.label}
                className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    {model.label}
                  </span>
                  <span className="font-mono text-xs text-blue-500">{model.value}</span>
                </div>
                <p className="text-xs text-slate-400 dark:text-slate-500">{model.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* About */}
        <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 transition-theme">
          <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-3">
            About VeriClaim
          </h2>
          <div className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
            <p>
              <span className="font-medium text-slate-800 dark:text-slate-200">Version:</span> 1.0.0
            </p>
            <p>
              <span className="font-medium text-slate-800 dark:text-slate-200">Stack:</span>{" "}
              React + TypeScript + Tailwind (frontend), FastAPI + PyTorch (backend)
            </p>
            <p>
              <span className="font-medium text-slate-800 dark:text-slate-200">Pipeline:</span>{" "}
              PDF → Claims → Citations → Retrieval → NLI → Numerical → Verdict
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
