import { useEffect, useEffectEvent, useState } from "react";

export function useResource<T>(key: string, loader: () => Promise<T>) {
  const load = useEffectEvent(loader);
  const [attempt, setAttempt] = useState(0);
  const requestKey = `${key}:${attempt}`;
  const [snapshot, setSnapshot] = useState<{ key: string; data?: T; error?: unknown }>({ key: "" });
  useEffect(() => {
    let active = true;
    load()
      .then((data) => {
        if (active) setSnapshot({ key: requestKey, data });
      })
      .catch((error) => {
        if (active) setSnapshot({ key: requestKey, error });
      });
    return () => {
      active = false;
    };
  }, [requestKey]);
  return {
    data: snapshot.key === requestKey ? snapshot.data : undefined,
    error: snapshot.key === requestKey ? snapshot.error : undefined,
    loading: snapshot.key !== requestKey,
    retry: () => setAttempt((n) => n + 1),
  };
}
