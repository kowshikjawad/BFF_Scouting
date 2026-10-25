import { avatarColor, initials } from "../lib/avatar";

export function Avatar({ id, name, size = 44 }: { id: string; name: string; size?: number }) {
  const color = avatarColor(id);
  return (
    <div
      className="flex shrink-0 items-center justify-center rounded-[6px] font-display font-semibold"
      style={{
        width: size,
        height: size,
        backgroundColor: `${color}26`,
        color,
        fontSize: size * 0.36,
        border: `1px solid ${color}4d`,
      }}
      aria-hidden="true"
    >
      {initials(name)}
    </div>
  );
}
