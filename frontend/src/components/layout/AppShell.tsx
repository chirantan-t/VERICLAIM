/**
 * AppShell: main layout component with sidebar + topbar + content area.
 */

import { useState } from "react";
import { Outlet } from "react-router-dom";
import type { AnalysisResponse } from "../../types/api";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

interface AppShellProps {
  isDark: boolean;
  onThemeToggle: () => void;
  analysisData: AnalysisResponse | null;
}

export default function AppShell({
  isDark,
  onThemeToggle,
  analysisData,
}: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const documentTitle = analysisData?.document?.metadata?.title ?? undefined;
  const processingStatus =
    analysisData?.processing_status?.stage === "complete"
      ? undefined
      : analysisData?.processing_status?.message;

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-slate-950 transition-theme">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        hasAnalysis={!!analysisData}
      />

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar
          onMenuClick={() => setSidebarOpen(true)}
          isDark={isDark}
          onThemeToggle={onThemeToggle}
          documentTitle={documentTitle}
          processingStatus={processingStatus}
        />

        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
