import { NavLink, Outlet } from "react-router-dom";
import { ShieldCheck, Users } from "lucide-react";

const navItems = [
  { to: "/", label: "Search", icon: Users },
  { to: "/eligibility", label: "Eligibility", icon: ShieldCheck },
];

export function Shell() {
  return (
    <div className="min-h-screen bg-shell">
      <header className="sticky top-0 z-10 border-b border-border bg-shell/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center gap-8 px-6 py-4">
          <div className="flex items-baseline gap-2">
            <span className="font-display text-lg font-semibold tracking-tight text-ink">
              ShonarTalent
            </span>
            <span className="font-display text-lg font-semibold text-pitch">AI</span>
          </div>
          <nav className="flex items-center gap-1">
            {navItems.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-[6px] px-3 py-1.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-surface-raised text-ink"
                      : "text-ink-muted hover:text-ink"
                  }`
                }
              >
                <Icon size={16} strokeWidth={2} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
