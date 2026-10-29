import { createContext, useContext } from "react";
export type Dataset = "real" | "synthetic";
export const DATASET_KEY = "shonartalent.dataset.v1";
export function sourceFromId(id: string): Dataset {
  return id.startsWith("synthetic-v1-") ? "synthetic" : "real";
}
export const DatasetContext = createContext<{
  dataset: Dataset;
  selectDataset: (dataset: Dataset) => void;
  pathFor: (path: string) => string;
}>({ dataset: "synthetic", selectDataset: () => {}, pathFor: (path) => path });
export const useDataset = () => useContext(DatasetContext);
