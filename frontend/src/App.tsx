import { lazy, Suspense } from "react";
import { Link, Route, Routes } from "react-router-dom";
import { Shell } from "./components/Shell";
import { SearchPage } from "./pages/SearchPage";
import { DatasetProvider } from "./lib/DatasetProvider";
import { ShortlistProvider } from "./lib/shortlist";
const ProfilePage = lazy(() =>
  import("./pages/ProfilePage").then((m) => ({ default: m.ProfilePage })),
);
const EligibilityPage = lazy(() =>
  import("./pages/EligibilityPage").then((m) => ({ default: m.EligibilityPage })),
);
const GuidePage = lazy(() => import("./pages/GuidePage").then((m) => ({ default: m.GuidePage })));
export default function App() {
  return (
    <DatasetProvider>
      <ShortlistProvider>
        <Suspense
          fallback={
            <p className="p-10 text-sm text-ink-muted" role="status">
              Loading workspace…
            </p>
          }
        >
          <Routes>
            <Route element={<Shell />}>
              <Route path="/" element={<SearchPage />} />
              <Route path="/shortlist" element={<SearchPage shortlist />} />
              <Route path="/players/:id" element={<ProfilePage />} />
              <Route path="/eligibility" element={<EligibilityPage />} />
              <Route path="/guide" element={<GuidePage />} />
              <Route
                path="*"
                element={
                  <div className="panel py-24 text-center">
                    <h1 className="page-title">Page not found</h1>
                    <p className="page-description">
                      Return to the workspace to continue scouting.
                    </p>
                    <Link className="btn mt-6" to="/">
                      Player discovery
                    </Link>
                  </div>
                }
              />
            </Route>
          </Routes>
        </Suspense>
      </ShortlistProvider>
    </DatasetProvider>
  );
}
