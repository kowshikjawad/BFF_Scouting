import { useDataset } from "../lib/dataset-context";
import { Link } from "react-router-dom";
import { Bookmark, Database, FileText, Globe2, ShieldCheck } from "lucide-react";
export function GuidePage() {
  const { pathFor } = useDataset();
  return (
    <div className="max-w-4xl">
      <h1 className="page-title">
        Workspace guide<span className="text-pitch">.</span>
      </h1>
      <p className="page-description">A practical guide to scouting with ShonarTalent AI.</p>
      <section className="panel relative mt-7 overflow-hidden p-6 sm:p-8">
        <img
          src="/accents/header-motif.webp"
          alt=""
          aria-hidden="true"
          className="pointer-events-none absolute -right-4 -top-10 z-0 hidden h-[180%] w-auto opacity-60 md:block"
        />
        <div className="relative z-10">
          <h2 className="font-display text-xl font-medium">How the synthetic demo works</h2>
          <ol className="mt-5 space-y-4 text-xs leading-7 text-ink-muted">
            <li>
              <strong className="text-ink">1. Explore 160 fictional players.</strong> Four demo
              leagues and 10 positions give you complete profiles to search and filter. Every
              person, club, value and performance figure in this view is invented.
            </li>
            <li>
              <strong className="text-ink">2. Read the five metrics.</strong> Goals, key passes,
              progressive carries and tackles are rates per 90 minutes. Aerial duels is a
              percentage. Values vary by position and style, rather than unrelated random numbers.
            </li>
            <li>
              <strong className="text-ink">3. Open a tactical profile.</strong> The radar puts each
              metric on a 0–100 percentile scale against the four demo players in the same league
              and position. The gray shape is their median. Raw values appear below.
            </li>
            <li>
              <strong className="text-ink">4. Find similar players.</strong> The engine standardizes
              the five metrics and compares the direction of each performance vector using cosine
              similarity. It returns five closest profiles from the same data source. A high score
              means a similar statistical shape, not a prediction of quality or success.
            </li>
            <li>
              <strong className="text-ink">5. Save, screen and export.</strong> Bookmark prospects,
              try the three fictional eligibility scenarios, and download a one-page report labelled
              synthetic. Use Data source in the navigation to return to real records.
            </li>
          </ol>
          <div className="mt-5 flex flex-wrap gap-3">
            <Link className="btn btn-primary" to="/players/synthetic-v1-001">
              Open a complete demo profile
            </Link>
            <Link className="btn" to="/eligibility?dataset=synthetic">
              Try eligibility examples
            </Link>
          </div>
          <p className="mt-4 text-[11px] leading-relaxed text-ink-muted">
            Demo figures are reproducible from a fixed generation seed. The original real-player
            data stays unchanged, and analytics never mix the two datasets.
          </p>
        </div>
      </section>
      <div className="mt-8 grid gap-5 sm:grid-cols-2">
        {[
          {
            icon: Database,
            title: "Discover & narrow",
            text: "Search names, combine position and age filters, and sort by value. Position filters include secondary roles. Your search stays in the URL so you can return to it.",
            to: "/",
            action: "Discover players",
          },
          {
            icon: Bookmark,
            title: "Build your shortlist",
            text: "Bookmark promising players from the directory or a profile. Saved players stay in this browser; they are not shared between devices or teammates.",
            to: "/shortlist",
            action: "Open shortlist",
          },
          {
            icon: ShieldCheck,
            title: "Screen known facts",
            text: "The checker helps organize ancestry, residency and representation facts. Its simplified legacy screening needs confirmation under current FIFA regulations.",
            to: "/eligibility",
            action: "Check eligibility",
          },
          {
            icon: FileText,
            title: "Take a report with you",
            text: "Open a player profile and select Export report to download a one-page PDF with recorded facts, metrics and coverage notes.",
            to: "/",
            action: "Choose a player",
          },
        ].map(({ icon: Icon, title, text, to, action }) => (
          <section key={title} className="panel p-6">
            <Icon size={22} strokeWidth={1.5} className="mb-4 text-pitch" />
            <h2 className="font-display text-lg font-medium">{title}</h2>
            <p className="mt-2 text-xs leading-7 text-ink-muted">{text}</p>
            <Link
              to={pathFor(to)}
              className="mt-4 inline-block text-xs font-medium text-pitch underline underline-offset-2"
            >
              {action}
            </Link>
          </section>
        ))}
      </div>
      <section className="panel mt-6 p-6 sm:p-8">
        <Globe2 size={22} className="mb-4 text-pitch" />
        <h2 className="font-display text-xl font-medium">Know your data.</h2>
        <div className="mt-5 space-y-5 text-xs leading-7 text-ink-muted">
          <p>
            <strong className="font-medium text-ink">Player records.</strong> Domestic squad
            profiles come from publicly available club and league listings. Diaspora records are a
            maintained reference roster with verification notes in the project. Source coverage
            varies and profiles are snapshots, not a live feed.
          </p>
          <p>
            <strong className="font-medium text-ink">Tactical coverage.</strong> Per-90 metrics
            depend on FBref’s competition coverage. Many tracked players have no recorded metrics. A
            dash means unrecorded. Charts require complete metrics and peers in the same league and
            position; similarity results depend on available data and may use mean imputation for
            partial profiles.
          </p>
          <p>
            <strong className="font-medium text-ink">Eligibility.</strong> A stored status reflects
            a recorded assessment, not proof of official clearance. The checker uses a simplified
            legacy ruleset; confirm nationality, documentation, residency and association switches
            with the federation.
          </p>
          <p>
            <strong className="font-medium text-ink">Player imagery.</strong> Initials identify
            players consistently. No stock or generated photograph is presented as a real player.
          </p>
        </div>
      </section>
      <section className="mt-8 border-t border-border pt-6">
        <p className="eyebrow mb-3">Open-source design assets</p>
        <p className="text-xs leading-7 text-ink-muted">
          <a
            href="https://lucide.dev/license"
            target="_blank"
            rel="noreferrer"
            className="text-pitch underline"
          >
            Lucide icons
          </a>{" "}
          (ISC / MIT),{" "}
          <a
            href="https://rsms.me/inter/"
            target="_blank"
            rel="noreferrer"
            className="text-pitch underline"
          >
            Inter
          </a>{" "}
          and{" "}
          <a
            href="https://github.com/floriankarsten/space-grotesk"
            target="_blank"
            rel="noreferrer"
            className="text-pitch underline"
          >
            Space Grotesk
          </a>{" "}
          (SIL Open Font License). Fonts and icons are bundled locally.{" "}
          <a href="/licenses/ASSET-CREDITS.txt" className="text-pitch underline">
            License notices
          </a>
          .
        </p>
      </section>
    </div>
  );
}
