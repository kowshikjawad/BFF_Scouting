import { useEffect, useRef, useState } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { Bookmark, BookOpen, ChevronRight, Menu, ScanLine, ShieldCheck, X } from "lucide-react";
import { useDataset, sourceFromId } from "../lib/dataset-context";
import { useShortlist } from "../lib/shortlist-context";

const nav = [
  { to: "/", label: "Player discovery", icon: ScanLine },
  { to: "/shortlist", label: "My shortlist", icon: Bookmark },
  { to: "/eligibility", label: "Eligibility checker", icon: ShieldCheck },
];
export function Shell() {
  const { ids, warning } = useShortlist();
  const { dataset, selectDataset, pathFor } = useDataset();
  const savedCount = ids.filter((id) => sourceFromId(id) === dataset).length;
  const location = useLocation();
  const [openedAt, setOpenedAt] = useState<string | null>(null);
  const open = openedAt === location.key;
  const menuButton = useRef<HTMLButtonElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const active =
    nav.find((n) => n.to === location.pathname)?.label ??
    (location.pathname.startsWith("/players/") ? "Player profile" : "Workspace guide");
  useEffect(() => {
    document.title = `${active} · ShonarTalent AI`;
    window.scrollTo(0, 0);
  }, [active, location.pathname]);
  useEffect(() => {
    if (open) closeButton.current?.focus();
    const previousOverflow = document.body.style.overflow;
    if (open) document.body.style.overflow = "hidden";
    function handle(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setOpenedAt(null);
        requestAnimationFrame(() => menuButton.current?.focus());
      }
    }
    window.addEventListener("keydown", handle);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", handle);
    };
  }, [open]);
  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      {open && (
        <button
          tabIndex={-1}
          aria-label="Close navigation overlay"
          onClick={() => setOpenedAt(null)}
          className="fixed inset-0 z-20 bg-ink/30 mobile-only"
        />
      )}
      <aside
        className={`sidebar ${open ? "open" : ""}`}
        aria-label="Workspace navigation"
        onKeyDown={(event) => {
          if (!open || event.key !== "Tab") return;
          const items = Array.from(
            event.currentTarget.querySelectorAll<HTMLElement>("a[href], button"),
          );
          const first = items[0],
            last = items.at(-1);
          if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last?.focus();
          } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first?.focus();
          }
        }}
      >
        <div className="flex h-[89px] items-center gap-2 px-6">
          <Link
            to={pathFor("/")}
            className="flex items-center gap-2.5"
            aria-label="ShonarTalent home"
          >
            <img src="/favicon.svg" alt="" aria-hidden="true" className="h-9 w-9 shrink-0" />
            <span className="font-display text-[18px] font-semibold tracking-tight">
              ShonarTalent<span className="ml-1 text-[10px] text-pitch">AI</span>
            </span>
          </Link>
          <button
            ref={closeButton}
            className="icon-button mobile-only"
            aria-label="Close navigation"
            onClick={() => {
              setOpenedAt(null);
              requestAnimationFrame(() => menuButton.current?.focus());
            }}
          >
            <X size={18} />
          </button>
        </div>
        <div className="mx-5 mb-7 rounded-control border border-border bg-shell px-3 py-3">
          <div className="flex items-center gap-2 text-xs font-medium">
            <span className="h-2 w-2 rounded-full bg-pitch" />
            Bangladesh scouting
          </div>
          <p className="mt-1.5 pl-4 text-[10px] text-ink-muted">Domestic & diaspora talent</p>
        </div>
        <label className="mx-5 mb-6 flex flex-col gap-2 text-[10px] font-medium text-ink-muted">
          Data source
          <select
            aria-label="Data source"
            value={dataset}
            onChange={(event) => selectDataset(event.target.value as "real" | "synthetic")}
          >
            <option value="synthetic">Synthetic demo</option>
            <option value="real">Real records</option>
          </select>
        </label>
        <div className="px-4">
          <p className="eyebrow mb-3 px-3">Workspace</p>
          <nav aria-label="Main navigation">
            {nav.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={pathFor(to)}
                end
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
              >
                <Icon size={17} strokeWidth={1.7} />
                <span>{label}</span>
                {to === "/shortlist" && (
                  <span className="ml-auto rounded bg-chip px-1.5 text-[10px]">{savedCount}</span>
                )}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="mt-auto px-4 pb-5 pt-8">
          <div className="relative mb-5 overflow-hidden rounded-panel bg-surface-raised p-4">
            <img
              src="/accents/promo-motif.svg"
              alt=""
              aria-hidden="true"
              className="pointer-events-none absolute -right-6 -top-6 h-28 w-28 opacity-70"
            />
            <p className="font-display text-sm font-medium">A wider view of talent.</p>
            <p className="mt-2 text-[11px] leading-relaxed text-ink-muted">
              Explore players at home and across borders, in one workspace.
            </p>
            <Link
              to={pathFor("/guide")}
              className="mt-3 inline-block text-[11px] font-medium text-pitch underline underline-offset-2"
            >
              About the data
            </Link>
          </div>
          <NavLink
            to={pathFor("/guide")}
            className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
          >
            <BookOpen size={17} />
            Workspace guide
          </NavLink>
          <div className="mt-4 border-t border-border px-3 pt-4 text-[10px] text-ink-muted">
            ShonarTalent AI <span className="float-right">v1.0</span>
          </div>
        </div>
      </aside>
      <div className="workspace" inert={open || undefined}>
        <header className="topbar">
          <div className="flex items-center gap-3">
            <button
              ref={menuButton}
              className="icon-button mobile-only"
              aria-label="Open navigation"
              aria-expanded={open}
              onClick={() => setOpenedAt(location.key)}
            >
              <Menu size={20} />
            </button>
            <span className="hidden text-xs text-ink-muted sm:block">Workspace</span>
            <ChevronRight size={13} className="hidden text-ink-faint sm:block" />
            <span className="text-xs font-medium">{active}</span>
          </div>
          <div className="flex items-center gap-2 text-[11px] text-ink-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-pitch" />
            <span className="hidden sm:inline">Scouting workspace</span>
            <span className="sm:hidden">ShonarTalent</span>
          </div>
        </header>
        <main id="main-content" className="main-content" tabIndex={-1}>
          {dataset === "synthetic" && (
            <div
              role="note"
              className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-panel border border-[var(--color-notice-border)] bg-[var(--color-notice)] px-4 py-3 text-[11px] leading-relaxed text-[var(--color-notice-ink)]"
            >
              <span>
                <strong>Synthetic demo</strong> · Fictional players, clubs and metrics for exploring
                the app.
              </span>
              <Link to={pathFor("/guide")} className="font-medium underline underline-offset-2">
                How it works
              </Link>
            </div>
          )}
          {warning && (
            <div role="status" className="mb-5 rounded-panel bg-gold-tint p-3 text-xs text-gold">
              {warning}
            </div>
          )}
          <Outlet />
        </main>
      </div>
    </>
  );
}
