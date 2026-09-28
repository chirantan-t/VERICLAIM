/**
 * Theme hook: manages dark/light mode with localStorage persistence.
 */

import { useCallback, useEffect, useState } from "react";

type Theme = "dark" | "light";

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === "undefined") return "dark";
    const stored = localStorage.getItem("vericlaim-theme") as Theme | null;
    if (stored) return stored;
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "dark"; // Default to dark
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("vericlaim-theme", theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === "dark" ? "light" : "dark"));
  }, []);

  const setTheme = useCallback((t: Theme) => {
    setThemeState(t);
  }, []);

  return { theme, toggleTheme, setTheme, isDark: theme === "dark" };
}
