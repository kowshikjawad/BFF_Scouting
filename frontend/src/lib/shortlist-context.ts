import { createContext, useContext } from "react";
export const KEY = "shonartalent.shortlist.v1";
export const Context = createContext<{
  ids: string[];
  toggle: (id: string) => void;
  warning: string | null;
}>({ ids: [], toggle: () => {}, warning: null });
export const useShortlist = () => useContext(Context);
