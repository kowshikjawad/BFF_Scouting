import { useState, type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { DatasetContext, DATASET_KEY, sourceFromId, type Dataset } from "./dataset-context";
export function DatasetProvider({ children }: { children: ReactNode }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [preference, setPreference] = useState<Dataset>(() => {
    try {
      return localStorage.getItem(DATASET_KEY) === "real" ? "real" : "synthetic";
    } catch {
      return "synthetic";
    }
  });
  const explicit = new URLSearchParams(location.search).get("dataset");
  // Profile provenance always wins, including an incorrectly supplied query string.
  const dataset = location.pathname.startsWith("/players/")
    ? sourceFromId(location.pathname.slice(9))
    : explicit === "real" || explicit === "synthetic"
      ? explicit
      : preference;
  function selectDataset(next: Dataset) {
    setPreference(next);
    try {
      localStorage.setItem(DATASET_KEY, next);
    } catch {
      /* URL preserves selection when storage is blocked. */
    }
    navigate(`/?dataset=${next}`);
  }
  function pathFor(path: string) {
    return `${path}${path.includes("?") ? "&" : "?"}dataset=${dataset}`;
  }
  return (
    <DatasetContext.Provider value={{ dataset, selectDataset, pathFor }}>
      {children}
    </DatasetContext.Provider>
  );
}
