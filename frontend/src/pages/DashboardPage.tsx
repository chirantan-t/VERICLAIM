/**
 * Dashboard page: analysis overview with statistics, charts, and claim list.
 */

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle,
  HelpCircle,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import {
  Bar,
  BarChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AnalysisResponse, VerdictType } from "../types/api";

interface DashboardPageProps {
  analysisData: AnalysisResponse | null;
}

const verdictConfig: Record<
  string,
  { color: string; bgClass: string; textClass: string; icon: typeof CheckCircle }
> = {
  SUPPORTED: {
    color: "#10b981",
    bgClass: "bg-emerald-50 dark:bg-emerald-900/20 border-emerald-200 dark:border-emerald-800/40",
    textClass: "text-emerald-700 dark:text-emerald-400",
    icon: CheckCircle,
  },
  PARTIALLY_SUPPORTED: {
    color: "#f59e0b",
    bgClass: "bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800/40",
    textClass: "text-amber-700 dark:text-amber-400",
    icon: AlertTriangle,
  },
  CONTRADICTED: {
    color: "#ef4444",
    bgClass: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800/40",
    textClass: "text-red-700 dark:text-red-400",
    icon: XCircle,
  },
  "INSUFFICIENT_EVIDENCE": {
    color: "#64748b",
    bgClass: "bg-slate-50 dark:bg-slate-800/60 border-slate-200 dark:border-slate-700/50",
    textClass: "text-slate-600 dark:text-slate-400",
    icon: HelpCircle,
  },
  SOURCE_UNAVAILABLE: {
    color: "#8b5cf6",
    bgClass: "bg-violet-50 dark:bg-violet-900/20 border-violet-200 dark:border-violet-800/40",
    textClass: "text-violet-700 dark:text-violet-400",
    icon: AlertTriangle,
  },
};

export default function DashboardPage({ analysisData }: DashboardPageProps) {
  const navigate = useNavigate();

  if (!analysisData) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center">
        <ShieldCheck className="w-12 h-12 text-slate-300 dark:text-slate-600 mb-4" />
        <h2 className="text-lg font-semibold text-slate-900 dark:text-white mb-2">
          No Analysis Yet
        </h2>
        <p className="text-slate-500 dark:text-slate-400 mb-6">
          Upload and analyze a paper to see verification results here.
        </p>
        <button
          onClick={() => navigate("/analyze")}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Analyze a Paper
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    );
  }

  const { statistics: stats, results } = analysisData;

  // Chart data
  const verdictData = Object.entries(stats.verdict_distribution).map(([name, value]) => ({
    name: name === "PARTIALLY_SUPPORTED" ? "Partial" : name === "INSUFFICIENT_EVIDENCE" ? "Insufficient" : name === "SOURCE_UNAVAILABLE" ? "Unavail" : name.charAt(0) + name.slice(1).toLowerCase(),
    value,
    color: verdictConfig[name]?.color || "#94a3b8",
  }));

  const typeData = Object.entries(stats.claim_type_distribution).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value,
  }));

  const confidenceData = results.map((r, i) => ({
    name: `#${i + 1}`,
    confidence: Math.round(r.confidence * 100),
    verdict: r.verdict,
  }));

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-[1400px] mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
            Verification Dashboard
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {analysisData.document.metadata.title || "Untitled Document"}
          </p>
        </div>
        <button
          onClick={() => navigate("/claims")}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors self-start"
        >
          Explore Claims
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 sm:gap-4">
        {[
          { label: "Claims", value: stats.total_claims, accent: "text-blue-500" },
          { label: "Resolved", value: stats.resolved_citations || 0, accent: "text-emerald-500" },
          { label: "Unresolved", value: stats.unresolved_citations || 0, accent: "text-red-500" },
          { label: "Citations", value: stats.total_citations, accent: "text-indigo-500" },
          { label: "Evidence", value: stats.total_evidence, accent: "text-violet-500" },
          { label: "Avg Conf", value: `${(stats.average_confidence * 100).toFixed(0)}%`, accent: "text-cyan-500" },
        ].map((s) => (
          <div
            key={s.label}
            className="p-4 sm:p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 transition-theme"
          >
            <p className="text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-2">
              {s.label}
            </p>
            <p className={`text-2xl sm:text-3xl font-bold ${s.accent}`}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Verdict cards */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
        {(["SUPPORTED", "PARTIALLY_SUPPORTED", "CONTRADICTED", "INSUFFICIENT_EVIDENCE", "SOURCE_UNAVAILABLE"] as VerdictType[]).map(
          (v) => {
            const config = verdictConfig[v];
            const count = stats.verdict_distribution[v] || 0;
            return (
              <div
                key={v}
                className={`p-4 sm:p-5 rounded-xl border ${config.bgClass} transition-theme cursor-pointer hover:shadow-md`}
                onClick={() => navigate(`/claims?verdict=${encodeURIComponent(v)}`)}
              >
                <div className="flex items-center gap-2 mb-2">
                  <config.icon className={`w-4 h-4 ${config.textClass}`} />
                  <span className={`text-xs font-semibold uppercase tracking-wider ${config.textClass}`}>
                    {v === "PARTIALLY_SUPPORTED" ? "Partial" : v === "INSUFFICIENT_EVIDENCE" ? "Insufficient" : v === "SOURCE_UNAVAILABLE" ? "Unavail" : v}
                  </span>
                </div>
                <p className={`text-3xl font-bold ${config.textClass}`}>{count}</p>
              </div>
            );
          },
        )}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Verdict distribution */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 transition-theme">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
            Verdict Distribution
          </h3>
          {verdictData.length > 0 ? (
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={verdictData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                  stroke="none"
                >
                  {verdictData.map((entry, i) => (
                    <Cell key={i} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-surface, #fff)",
                    border: "1px solid var(--color-border, #e2e8f0)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[220px] flex items-center justify-center text-slate-400 text-sm">
              No data
            </div>
          )}
          <div className="flex flex-wrap gap-3 mt-2 justify-center">
            {verdictData.map((d) => (
              <div key={d.name} className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                {d.name} ({d.value})
              </div>
            ))}
          </div>
        </div>

        {/* Claim type distribution */}
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 transition-theme">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
            Claim Types
          </h3>
          {typeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={typeData} layout="vertical" margin={{ left: 10 }}>
                <XAxis type="number" hide />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={90}
                  tick={{ fontSize: 12, fill: "#94a3b8" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--color-surface, #fff)",
                    border: "1px solid var(--color-border, #e2e8f0)",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={18} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[250px] flex items-center justify-center text-slate-400 text-sm">
              No data
            </div>
          )}
        </div>
      </div>

      {/* Confidence distribution */}
      {confidenceData.length > 0 && (
        <div className="p-5 rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 transition-theme">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white mb-4">
            Confidence by Claim
          </h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={confidenceData}>
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-surface, #fff)",
                  border: "1px solid var(--color-border, #e2e8f0)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value: any) => [`${value}%`, "Confidence"]}
              />
              <Bar dataKey="confidence" radius={[3, 3, 0, 0]} barSize={24}>
                {confidenceData.map((entry, i) => (
                  <Cell key={i} fill={verdictConfig[entry.verdict]?.color || "#94a3b8"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Quick claim list */}
      <div className="rounded-xl bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 overflow-hidden transition-theme">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
            Verified Claims
          </h3>
          <button
            onClick={() => navigate("/claims")}
            className="text-xs font-medium text-blue-500 hover:text-blue-600 transition-colors"
          >
            View all →
          </button>
        </div>
        <div className="divide-y divide-slate-50 dark:divide-slate-800">
          {results.slice(0, 5).map((r, i) => {
            const config = verdictConfig[r.verdict] || verdictConfig["INSUFFICIENT EVIDENCE"];
            return (
              <div
                key={r.claim_id}
                className="px-5 py-4 flex items-start gap-4 hover:bg-slate-50 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                onClick={() => navigate(`/claims/${r.claim_id}`)}
              >
                <span className="text-xs font-mono text-slate-400 dark:text-slate-500 mt-1 shrink-0">
                  #{i + 1}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-slate-800 dark:text-slate-200 line-clamp-2">
                    {r.claim_text}
                  </p>
                  <div className="flex items-center gap-3 mt-2 flex-wrap">
                    <span className={`inline-flex items-center gap-1 text-xs font-semibold ${config.textClass}`}>
                      <config.icon className="w-3 h-3" />
                      {r.verdict}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">
                      {(r.confidence * 100).toFixed(0)}% confidence
                    </span>
                    {r.linked_citations.length > 0 && (
                      <span className="text-xs text-blue-400">
                        {r.linked_citations.join(", ")}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
