import { Bookmark, BookmarkCheck } from "lucide-react";
import { useShortlist } from "../lib/shortlist-context";
export function SaveButton({
  id,
  name,
  full = false,
}: {
  id: string;
  name: string;
  full?: boolean;
}) {
  const { ids, toggle } = useShortlist();
  const saved = ids.includes(id);
  const label = saved ? `Remove ${name} from shortlist` : `Save ${name} to shortlist`;
  return (
    <button
      type="button"
      onClick={() => toggle(id)}
      title={label}
      aria-label={label}
      aria-pressed={saved}
      className={`${full ? "btn" : "icon-button"} ${saved ? "text-pitch! bg-pitch-tint!" : ""}`}
    >
      {saved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
      {full && (saved ? "Saved to shortlist" : "Save player")}
    </button>
  );
}
