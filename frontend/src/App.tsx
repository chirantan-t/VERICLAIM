/**
 * Main application component: sets up routing and state management.
 */

import { useCallback, useState } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import AppShell from "./components/layout/AppShell";
import { useTheme } from "./hooks/useTheme";
import AnalyzePage from "./pages/AnalyzePage";
import CitationExplorerPage from "./pages/CitationExplorerPage";
import ClaimDetailPage from "./pages/ClaimDetailPage";
import ClaimExplorerPage from "./pages/ClaimExplorerPage";
import DashboardPage from "./pages/DashboardPage";
import EvidenceViewerPage from "./pages/EvidenceViewerPage";
import ExperimentsPage from "./pages/ExperimentsPage";
import HomePage from "./pages/HomePage";
import ResearchGraphPage from "./pages/ResearchGraphPage";
import SettingsPage from "./pages/SettingsPage";
import type { AnalysisResponse } from "./types/api";

function App() {
  const { isDark, toggleTheme } = useTheme();
  const [analysisData, setAnalysisData] = useState<AnalysisResponse | null>(null);

  const handleAnalysisComplete = useCallback((data: AnalysisResponse) => {
    setAnalysisData(data);
  }, []);

  return (
    <Router>
      <Routes>
        <Route
          element={
            <AppShell
              isDark={isDark}
              onThemeToggle={toggleTheme}
              analysisData={analysisData}
            />
          }
        >
          <Route path="/" element={<HomePage analysisData={analysisData} />} />
          <Route
            path="/analyze"
            element={<AnalyzePage onAnalysisComplete={handleAnalysisComplete} />}
          />
          <Route
            path="/dashboard"
            element={<DashboardPage analysisData={analysisData} />}
          />
          <Route
            path="/claims"
            element={<ClaimExplorerPage analysisData={analysisData} />}
          />
          <Route
            path="/claims/:claimId"
            element={<ClaimDetailPage analysisData={analysisData} />}
          />
          <Route
            path="/evidence"
            element={<EvidenceViewerPage analysisData={analysisData} />}
          />
          <Route
            path="/citations"
            element={<CitationExplorerPage analysisData={analysisData} />}
          />
          <Route path="/experiments" element={<ExperimentsPage />} />
          <Route
            path="/graph"
            element={<ResearchGraphPage analysisData={analysisData} />}
          />
          <Route
            path="/settings"
            element={<SettingsPage isDark={isDark} onThemeToggle={toggleTheme} />}
          />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
