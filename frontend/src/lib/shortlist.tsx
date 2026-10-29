import { useEffect, useState, type ReactNode } from "react";

import { Context, KEY } from "./shortlist-context";
import { parseShortlist } from "./shortlist-storage";
function read() {
  try {
    return parseShortlist(localStorage.getItem(KEY));
  } catch {
    return [];
  }
}
export function ShortlistProvider({ children }: { children: ReactNode }) {
  const [ids, setIds] = useState(read);
  const [warning, setWarning] = useState<string | null>(null);
  useEffect(() => {
    const sync = (event: StorageEvent) => {
      if (event.key === KEY || event.key === null) setIds(read());
    };
    window.addEventListener("storage", sync);
    return () => window.removeEventListener("storage", sync);
  }, []);
  function toggle(id: string) {
    const next = ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id].slice(0, 500);
    setIds(next);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
      setWarning(null);
    } catch {
      setWarning("Browser storage is unavailable. Your shortlist will last for this session only.");
    }
  }
  return <Context.Provider value={{ ids, toggle, warning }}>{children}</Context.Provider>;
}
