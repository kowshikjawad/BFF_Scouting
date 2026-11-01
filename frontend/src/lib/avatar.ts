// Generated initials avatars, deterministic per player id -- no stock or
// AI-generated photos are attached to a real player's profile (see
// PRODUCT.md Capabilities and Constraints).

const PALETTE = ["#4ade80", "#a3e635", "#fbbf24", "#60a5fa", "#c084fc", "#fb7185", "#2dd4bf"];

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
