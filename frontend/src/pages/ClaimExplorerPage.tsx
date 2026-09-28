/**
 * Claim Explorer page: filterable, sortable table of all verified claims.
 */

import {
  AlertTriangle,
  ArrowUpDown,
  CheckCircle,
  Filter,
  HelpCircle,
  Search,
  XCircle,
} from "lucide-react";
import { useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import type { AnalysisResponse } from "../types/api";

interface ClaimExplorerPageProps {
  analysisData: AnalysisResponse | null;
}

const verdictIcons: Record<string, typeof CheckCircle> = {
  SUPPORTED: CheckCircle,
  "PARTIALLY_SUPPORTED": AlertTriangle,
  CONTRADICTED: XCircle,
  "INSUFFICIENT_EVIDENCE": HelpCircle,
  "SOURCE_UNAVAILABLE": AlertTriangle,
};

const verdictColors: Record<string, string> = {
  SUPPORTED: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/20",
  "PARTIALLY_SUPPORTED": "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20",
  CONTRADICTED: "text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20",
  "INSUFFICIENT_EVIDENCE": "text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-800",
  "SOURCE_UNAVAILABLE": "text-violet-600 dark:text-violet-400 bg-violet-50 dark:bg-violet-900/20",
};

const claimTypeColors: Record<string, string> = {
  factual: "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400",
  numerical: "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400",
  comparative: "bg-violet-50 dark:bg-violet-900/20 text-violet-600 dark:text-violet-400",
  causal: "bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400",
  methodological: "bg-teal-50 dark:bg-teal-900/20 text-teal-600 dark:text-teal-400",
  statistical: "bg-indigo-50 dark:bg-indigo-900/20 text-indigo-600 dark:text-indigo-400",
  conclusion: "bg-pink-50 dark:bg-pink-900/20 text-pink-600 dark:text-pink-400",
};

type SortField = "confidence" | "verdict" | "type" | "section";

export default function ClaimExplorerPage({ analysisData }: ClaimExplorerPageProps) {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialVerdict = searchParams.get("verdict") || "";

  const [search, setSearch] = useState("");
  const [verdictFilter, setVerdictFilter] = useState<string>(initialVerdict);
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [sectionFilter, setSectionFilter] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>("confidence");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [showFilters, setShowFilters] = useState(!!initialVerdict);

  const results = analysisData?.results || [];

  // Get unique values for filters
  const sections = useMemo(() => {
    const set = new Set(results.map((r) => r.section || "Unknown"));
    return Array.from(set).sort();
  }, [results]);

  const claimTypes = useMemo(() => {
    const set = new Set(results.map((r) => r.claim_type));
    return Array.from(set).sort();
  }, [results]);

  // Filter & sort
  const filteredResults = useMemo(() => {
    let filtered = [...results];

    if (search) {
      const q = search.toLowerCase();
      filtered = filtered.filter(
        (r) =>
          r.claim_text.toLowerCase().includes(q) ||
          r.linked_citations.some((c) => c.toLowerCase().includes(q)),
      );
    }
    if (verdictFilter) {
      filtered = filtered.filter((r) => r.verdict === verdictFilter);
    }
    if (typeFilter) {
      filtered = filtered.filter((r) => r.claim_type === typeFilter);
    }
    if (sectionFilter) {
      filtered = filtered.filter((r) => (r.section || "Unknown") === sectionFilter);
    }

    filtered.sort((a, b) => {
      let cmp = 0;
      switch (sortField) {
        case "confidence":
          cmp = a.confidence - b.confidence;
          break;
        case "verdict":
          cmp = a.verdict.localeCompare(b.verdict);
          break;
        case "type":
          cmp = a.claim_type.localeCompare(b.claim_type);
          break;
        case "section":
          cmp = (a.section || "").localeCompare(b.section || "");
          break;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });

    return filtered;
  }, [results, search, verdictFilter, typeFilter, sectionFilter, sortField, sortDir]);

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  if (!analysisData) {
    return (
      <div className="flex items-center justify-center h-full p-8">
        <p className="text-slate-400">No analysis data. Upload a paper first.</p>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-[1400px] mx-auto animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
            Claim Explorer
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {filteredResults.length} of {results.length} claims
          </p>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="mb-4 space-y-3">
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search claims..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center gap-2 px-3 py-2.5 rounded-lg border text-sm font-medium transition-colors ${
              showFilters
                ? "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400"
                : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800"
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>

        {showFilters && (
          <div className="flex flex-wrap gap-3 animate-scale-in">
            <select
              value={verdictFilter}
              onChange={(e) => setVerdictFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 outline-none"
            >
              <option value="">All Verdicts</option>
              <option value="SUPPORTED">Supported</option>
              <option value="PARTIALLY_SUPPORTED">Partially Supported</option>
              <option value="CONTRADICTED">Contradicted</option>
              <option value="INSUFFICIENT_EVIDENCE">Insufficient Evidence</option>
              <option value="SOURCE_UNAVAILABLE">Source Unavailable</option>
            </select>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 outline-none"
            >
              <option value="">All Types</option>
              {claimTypes.map((t) => (
                <option key={t} value={t}>
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={sectionFilter}
              onChange={(e) => setSectionFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-700 dark:text-slate-300 outline-none"
            >
              <option value="">All Sections</option>
              {sections.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            {(verdictFilter || typeFilter || sectionFilter) && (
              <button
                onClick={() => { setVerdictFilter(""); setTypeFilter(""); setSectionFilter(""); }}
                className="px-3 py-2 text-xs font-medium text-red-500 hover:text-red-600 transition-colors"
              >
                Clear filters
              </button>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="rounded-xl border border-slate-200 dark:border-slate-800 overflow-hidden bg-white dark:bg-slate-900 transition-theme">
        {/* Header */}
        <div className="hidden md:grid grid-cols-[1fr_100px_110px_130px_100px] gap-4 px-5 py-3 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
          <span>Claim</span>
          <button onClick={() => toggleSort("type")} className="flex items-center gap-1 hover:text-slate-600">
            Type <ArrowUpDown className="w-3 h-3" />
          </button>
          <span>Citation</span>
          <button onClick={() => toggleSort("verdict")} className="flex items-center gap-1 hover:text-slate-600">
            Verdict <ArrowUpDown className="w-3 h-3" />
          </button>
          <button onClick={() => toggleSort("confidence")} className="flex items-center gap-1 hover:text-slate-600">
            Confidence <ArrowUpDown className="w-3 h-3" />
          </button>
        </div>

        {/* Rows */}
        <div className="divide-y divide-slate-50 dark:divide-slate-800">
          {filteredResults.map((r) => {
            const Icon = verdictIcons[r.verdict] || HelpCircle;
            const colorClass = verdictColors[r.verdict] || verdictColors["INSUFFICIENT_EVIDENCE"];
            const typeColor = claimTypeColors[r.claim_type] || claimTypeColors.factual;

            return (
              <div
                key={r.claim_id}
                onClick={() => navigate(`/claims/${r.claim_id}`)}
                className="px-5 py-4 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors md:grid md:grid-cols-[1fr_100px_110px_130px_100px] md:gap-4 md:items-center"
              >
                {/* Claim text */}
                <div className="min-w-0">
                  <p className="text-sm text-slate-800 dark:text-slate-200 line-clamp-2">
                    {r.claim_text}
                  </p>
                  {r.warnings.length > 0 && (
                    <span className="inline-flex items-center gap-1 text-[10px] font-medium text-amber-500 mt-1">
                      <AlertTriangle className="w-3 h-3" />
                      {r.warnings.length} warning{r.warnings.length > 1 ? "s" : ""}
                    </span>
                  )}
                </div>

                {/* Type */}
                <div className="mt-2 md:mt-0">
                  <span className={`inline-flex px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wider ${typeColor}`}>
                    {r.claim_type}
                  </span>
                </div>

                {/* Citations */}
                <div className="mt-1 md:mt-0 flex gap-1 flex-wrap">
                  {r.linked_citations.map((c) => (
                    <span key={c} className="text-xs font-medium text-blue-500 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20 px-1.5 py-0.5 rounded">
                      {c}
                    </span>
                  ))}
                </div>

                {/* Verdict */}
                <div className="mt-2 md:mt-0">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${colorClass}`}>
                    <Icon className="w-3 h-3" />
                    {r.verdict === "PARTIALLY_SUPPORTED" ? "Partial" : r.verdict === "INSUFFICIENT_EVIDENCE" ? "Insufficient" : r.verdict === "SOURCE_UNAVAILABLE" ? "Unavail" : r.verdict}
                  </span>
                </div>

                {/* Confidence */}
                <div className="mt-1 md:mt-0">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all"
                        style={{
                          width: `${r.confidence * 100}%`,
                          backgroundColor: r.confidence > 0.7 ? "#10b981" : r.confidence > 0.4 ? "#f59e0b" : "#ef4444",
                        }}
                      />
                    </div>
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400 w-8 text-right">
                      {(r.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}

          {filteredResults.length === 0 && (
            <div className="px-5 py-12 text-center text-slate-400 dark:text-slate-500 text-sm">
              No claims match your filters.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
