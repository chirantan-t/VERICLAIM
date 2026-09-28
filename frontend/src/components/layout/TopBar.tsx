/**
 * Top bar component with document info, search, and theme toggle.
 */

import { Menu, Moon, Sun, Wifi, WifiOff } from "lucide-react";
import { useEffect, useState } from "react";
import { healthCheck } from "../../lib/api";

interface TopBarProps {
  onMenuClick: () => void;
  isDark: boolean;
  onThemeToggle: () => void;
  documentTitle?: string;
  processingStatus?: string;
}

export default function TopBar({
  onMenuClick,
  isDark,
  onThemeToggle,
  documentTitle,
  processingStatus,
}: TopBarProps) {
  const [backendStatus, setBackendStatus] = useState<"ok" | "error" | "checking">("checking");

  useEffect(() => {
    healthCheck()
      .then(() => setBackendStatus("ok"))
      .catch(() => setBackendStatus("error"));
  }, []);

  return (
    <header
      className="h-16 border-b flex items-center justify-between px-4 sm:px-6 shrink-0
        bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800
        transition-theme"
    >
      {/* Left side */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle sidebar"
        >
          <Menu className="w-5 h-5 text-slate-600 dark:text-slate-400" />
        </button>

        {documentTitle && (
          <div className="hidden sm:flex items-center gap-2 min-w-0">
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400 dark:text-slate-500 shrink-0">
              Document
            </span>
            <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[300px]">
              {documentTitle}
            </span>
          </div>
        )}

        {processingStatus && (
          <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 animate-pulse-subtle">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            {processingStatus}
          </span>
        )}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Backend status */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium ${
            backendStatus === "ok"
              ? "text-emerald-600 dark:text-emerald-400"
              : backendStatus === "error"
                ? "text-red-500 dark:text-red-400"
                : "text-slate-400"
          }`}
          title={
            backendStatus === "ok"
              ? "Backend connected"
              : backendStatus === "error"
                ? "Backend unreachable"
                : "Checking backend..."
          }
        >
          {backendStatus === "ok" ? (
            <Wifi className="w-3.5 h-3.5" />
          ) : (
            <WifiOff className="w-3.5 h-3.5" />
          )}
          <span className="hidden sm:inline">
            {backendStatus === "ok" ? "Connected" : backendStatus === "error" ? "Disconnected" : "..."}
          </span>
        </div>

        {/* Theme toggle */}
        <button
          onClick={onThemeToggle}
          className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
        >
          {isDark ? (
            <Sun className="w-4.5 h-4.5 text-slate-400 hover:text-amber-400 transition-colors" />
          ) : (
            <Moon className="w-4.5 h-4.5 text-slate-500 hover:text-slate-700 transition-colors" />
          )}
        </button>
      </div>
    </header>
  );
}
