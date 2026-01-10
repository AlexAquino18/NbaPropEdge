import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Prop } from '@/types';

const PROJECTION_CACHE_KEY = 'projectionCache:v1';

type ProjectionSnapshot = Pick<Prop, 'id' | 'projection' | 'probability_over' | 'edge' | 'confidence'>;

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getProjectionCache(): Record<string, ProjectionSnapshot> {
  try {
    const raw = localStorage.getItem(PROJECTION_CACHE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

export function setProjectionCache(cache: Record<string, ProjectionSnapshot>) {
  try {
    localStorage.setItem(PROJECTION_CACHE_KEY, JSON.stringify(cache));
  } catch {
    // ignore write errors
  }
}

export function updateProjectionCacheFromProps(props: Prop[]) {
  const cache = getProjectionCache();
  props.forEach((p) => {
    // Only cache projections for active props (still in DB list)
    cache[p.id] = {
      id: p.id,
      projection: p.projection ?? cache[p.id]?.projection ?? null,
      probability_over: p.probability_over ?? cache[p.id]?.probability_over ?? null,
      edge: p.edge ?? cache[p.id]?.edge ?? null,
      confidence: p.confidence ?? cache[p.id]?.confidence ?? null,
    } as ProjectionSnapshot;
  });
  setProjectionCache(cache);
}

export function mergePropsWithProjectionCache(props: Prop[]): Prop[] {
  const cache = getProjectionCache();
  return props.map((p) => {
    const snap = cache[p.id];
    if (!snap) return p;
    // Preserve projections if present in cache and prop is still active
    return {
      ...p,
      projection: snap.projection ?? p.projection,
      probability_over: snap.probability_over ?? p.probability_over,
      edge: snap.edge ?? p.edge,
      confidence: snap.confidence ?? p.confidence,
    };
  });
}
