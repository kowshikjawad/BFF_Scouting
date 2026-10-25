import { Route, Routes } from "react-router-dom";
import { Shell } from "./components/Shell";
import { SearchPage } from "./pages/SearchPage";
import { ProfilePage } from "./pages/ProfilePage";
import { EligibilityPage } from "./pages/EligibilityPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route path="/" element={<SearchPage />} />
        <Route path="/players/:id" element={<ProfilePage />} />
        <Route path="/eligibility" element={<EligibilityPage />} />
      </Route>
    </Routes>
  );
}
