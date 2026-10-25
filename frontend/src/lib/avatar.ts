// Generated initials avatars, deterministic per player id -- no stock or
// AI-generated photos are attached to a real player's profile (see
// PRODUCT.md Capabilities and Constraints).

const PALETTE = [
  "#22c55e", // pitch
  "#16a34a", // pitch strong
  "#d4a24c", // gold
  "#3b82f6",
  "#a855f7",
  "#ec4899",
  "#06b6d4",
];

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash << 5) - hash + value.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

export function avatarColor(id: string): string {
  return PALETTE[hashString(id) % PALETTE.length];
}

export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}
