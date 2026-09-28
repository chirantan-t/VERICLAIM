/**
 * Analyze page: PDF upload with drag-and-drop and processing progress.
 */

import {
  AlertTriangle,
  CheckCircle,
  FileText,
  Loader2,
  ShieldCheck,
  Upload,
  XCircle,
} from "lucide-react";
import React, { useCallback, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { uploadDocument } from "../lib/api";
import type { AnalysisResponse } from "../types/api";

interface AnalyzePageProps {
  onAnalysisComplete: (data: AnalysisResponse) => void;
}

const PROCESSING_STAGES = [
  { key: "parsing", label: "Parsing document" },
  { key: "extracting_citations", label: "Extracting citations" },
  { key: "detecting_claims", label: "Detecting claims" },
  { key: "linking_citations", label: "Linking citations" },
  { key: "retrieving_evidence", label: "Retrieving evidence" },
  { key: "semantic_analysis", label: "Running semantic analysis" },
  { key: "nli_verification", label: "Running NLI verification" },
  { key: "numerical_checking", label: "Checking numerical consistency" },
  { key: "generating_report", label: "Generating verification report" },
];

export default function AnalyzePage({ onAnalysisComplete }: AnalyzePageProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileSelect = useCallback((selectedFile: File) => {
    if (!selectedFile.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }
    if (selectedFile.size > 50 * 1024 * 1024) {
      setError("File too large. Maximum size is 50MB.");
      return;
    }
    setFile(selectedFile);
    setError(null);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    },
    [handleFileSelect],
  );

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError(null);
    setCurrentStage(0);

    // Simulate stage progression during upload
    const stageInterval = setInterval(() => {
      setCurrentStage((prev) =>
        prev < PROCESSING_STAGES.length - 1 ? prev + 1 : prev,
      );
    }, 2000);

    try {
      const data = await uploadDocument(file);
      clearInterval(stageInterval);
      setCurrentStage(PROCESSING_STAGES.length);
      onAnalysisComplete(data);
      setTimeout(() => navigate("/dashboard"), 500);
    } catch (err: any) {
      clearInterval(stageInterval);
      setError(err.message || "An error occurred during verification.");
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-10 sm:py-16 animate-fade-in">
      <div className="text-center mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white mb-2">
          Analyze a Paper
        </h1>
        <p className="text-slate-500 dark:text-slate-400">
          Upload a research PDF to extract and verify scientific claims.
        </p>
      </div>

      {/* Upload area */}
      {!isUploading ? (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm transition-theme">
          {/* Drop zone */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-xl p-10 sm:p-14 cursor-pointer
              flex flex-col items-center justify-center text-center
              transition-all duration-200
              ${isDragOver
                ? "border-blue-400 bg-blue-50 dark:bg-blue-900/20"
                : "border-slate-200 dark:border-slate-700 hover:border-blue-300 dark:hover:border-blue-600 hover:bg-slate-50 dark:hover:bg-slate-800/50"
              }
            `}
          >
            <Upload
              className={`w-10 h-10 mb-4 transition-colors ${isDragOver ? "text-blue-500" : "text-slate-400"}`}
            />
            <p className="text-sm font-semibold text-slate-900 dark:text-white mb-1">
              {isDragOver ? "Drop your PDF here" : "Drag and drop your PDF here"}
            </p>
            <p className="text-xs text-slate-400 dark:text-slate-500 mb-4">
              or click to browse · PDF only · max 50MB
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
              }}
            />
          </div>

          {/* File info */}
          {file && (
            <div className="mt-4 flex items-center justify-between bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700/50 p-4 rounded-xl animate-scale-in">
              <div className="flex items-center gap-3 min-w-0">
                <FileText className="w-5 h-5 text-blue-500 shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                    {file.name}
                  </p>
                  <p className="text-xs text-slate-400">
                    {formatFileSize(file.size)}
                  </p>
                </div>
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
                className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                aria-label="Remove file"
              >
                <XCircle className="w-4 h-4 text-slate-400" />
              </button>
            </div>
          )}

          {/* Upload button */}
          <button
            onClick={handleUpload}
            disabled={!file}
            className="mt-6 w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-lg shadow-blue-500/20 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none active:scale-[0.98]"
          >
            <ShieldCheck className="w-4.5 h-4.5" />
            Verify Claims
          </button>

          {error && (
            <div className="mt-4 flex items-start gap-2 p-4 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-sm border border-red-100 dark:border-red-800/40 animate-scale-in">
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>{error}</p>
            </div>
          )}
        </div>
      ) : (
        /* Processing progress */
        <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 sm:p-8 shadow-sm transition-theme animate-fade-in">
          <div className="flex items-center gap-3 mb-6">
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
              Analyzing Document
            </h2>
          </div>

          {/* Progress bar */}
          <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full mb-8 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-blue-400 rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${Math.min(((currentStage + 1) / PROCESSING_STAGES.length) * 100, 100)}%`,
              }}
            />
          </div>

          {/* Stage list */}
          <div className="space-y-3">
            {PROCESSING_STAGES.map((stage, i) => (
              <div
                key={stage.key}
                className={`flex items-center gap-3 py-2 px-3 rounded-lg transition-all duration-300 ${
                  i < currentStage
                    ? "text-emerald-600 dark:text-emerald-400"
                    : i === currentStage
                      ? "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20"
                      : "text-slate-300 dark:text-slate-600"
                }`}
              >
                {i < currentStage ? (
                  <CheckCircle className="w-4 h-4 shrink-0" />
                ) : i === currentStage ? (
                  <Loader2 className="w-4 h-4 shrink-0 animate-spin" />
                ) : (
                  <div className="w-4 h-4 rounded-full border-2 border-current shrink-0" />
                )}
                <span className="text-sm font-medium">{stage.label}</span>
              </div>
            ))}
          </div>

          {file && (
            <p className="mt-6 text-xs text-slate-400 dark:text-slate-500 text-center">
              Processing {file.name} · This may take a minute for large documents.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
