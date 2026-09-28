/**
 * Sidebar navigation component.
 * Always dark themed, with icon + label navigation items.
 */

import {
  BarChart3,
  BookOpen,
  FileSearch,
  FlaskConical,
  Home,
  Network,
  Quote,
  Settings,
  ShieldCheck,
  Upload,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  hasAnalysis: boolean;
}

const navItems = [
  { to: "/", icon: Home, label: "Overview", requiresAnalysis: false },
  {
    to: "/analyze",
    icon: Upload,
    label: "Analyze Paper",
    requiresAnalysis: false,
  },
  {
    to: "/dashboard",
    icon: BarChart3,
    label: "Dashboard",
    requiresAnalysis: true,
  },
  {
    to: "/claims",
    icon: FileSearch,
    label: "Claims",
    requiresAnalysis: true,
  },
  {
    to: "/evidence",
    icon: BookOpen,
    label: "Evidence",
    requiresAnalysis: true,
  },
  {
    to: "/citations",
    icon: Quote,
    label: "Citations",
    requiresAnalysis: true,
  },
  {
    to: "/experiments",
    icon: FlaskConical,
    label: "Experiments",
    requiresAnalysis: false,
  },
  {
    to: "/graph",
    icon: Network,
    label: "Research Graph",
    requiresAnalysis: true,
  },
  {
    to: "/settings",
    icon: Settings,
    label: "Settings",
    requiresAnalysis: false,
  },
];

export default function Sidebar({ isOpen, onClose, hasAnalysis }: SidebarProps) {
  return (
    <>
      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 h-full z-50 w-64
          bg-slate-950 text-slate-300
          flex flex-col
          transition-transform duration-300 ease-in-out
          lg:translate-x-0 lg:static lg:z-auto
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-5 border-b border-slate-800/80">
          <NavLink to="/" className="flex items-center gap-2.5 group" onClick={onClose}>
            <ShieldCheck className="w-7 h-7 text-blue-400 group-hover:text-blue-300 transition-colors" />
            <span className="text-lg font-bold tracking-tight text-white">
              VERI<span className="text-blue-400">CLAIM</span>
            </span>
          </NavLink>
          <button
            onClick={onClose}
            className="lg:hidden p-1 rounded hover:bg-slate-800 transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const isDisabled = item.requiresAnalysis && !hasAnalysis;
            return (
              <NavLink
                key={item.to}
                to={isDisabled ? "#" : item.to}
                onClick={(e) => {
                  if (isDisabled) {
                    e.preventDefault();
                    return;
                  }
                  onClose();
                }}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                    isDisabled
                      ? "text-slate-600 cursor-not-allowed"
                      : isActive
                        ? "bg-blue-600/20 text-blue-400 shadow-sm"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/80"
                  }`
                }
              >
                <item.icon className="w-[18px] h-[18px] shrink-0" />
                <span>{item.label}</span>
                {isDisabled && (
                  <span className="ml-auto text-[10px] uppercase tracking-wider text-slate-600">
                    analyze first
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-slate-800/80">
          <p className="text-xs text-slate-600">
            Scientific Claim Verification
          </p>
          <p className="text-[10px] text-slate-700 mt-0.5">v1.0.0</p>
        </div>
      </aside>
    </>
  );
}
