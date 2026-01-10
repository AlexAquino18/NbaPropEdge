import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import type { Prop } from '@/types';

const PROJECTION_CACHE_KEY = 'projectionCache:v1';
const LAST_PROPS_CACHE_KEY = 'lastPropsCache:v1';

type ProjectionSnapshot = Pick<Prop, 'external_id' | 'player_name' | 'stat_type' | 'line' | 'projection' | 'probability_over' | 'edge' | 'confidence'>;

function makePropKey(p: Prop): string {
  const base = p.external_id || `${p.player_name}|${p.stat_type}|${Number(p.line).toFixed(1)}`;
  return base;
}

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

export function getLastPropsCache(): Prop[] {
  try {
    const raw = localStorage.getItem(LAST_PROPS_CACHE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function setLastPropsCache(props: Prop[]) {
  try {
    localStorage.setItem(LAST_PROPS_CACHE_KEY, JSON.stringify(props));
  } catch {
    // ignore write errors
  }
}

export function updateProjectionCacheFromProps(props: Prop[]) {
  const cache = getProjectionCache();
  props.forEach((p) => {
    const key = makePropKey(p);
    cache[key] = {
      external_id: p.external_id ?? cache[key]?.external_id ?? null,
      player_name: p.player_name,
      stat_type: p.stat_type,
      line: p.line,
      projection: p.projection ?? cache[key]?.projection ?? null,
      probability_over: p.probability_over ?? cache[key]?.probability_over ?? null,
      edge: p.edge ?? cache[key]?.edge ?? null,
      confidence: p.confidence ?? cache[key]?.confidence ?? null,
    } as ProjectionSnapshot;
  });
  setProjectionCache(cache);
}

export function mergePropsWithProjectionCache(props: Prop[]): Prop[] {
  const cache = getProjectionCache();
  return props.map((p) => {
    const key = makePropKey(p);
    const snap = cache[key];
    if (!snap) return p;
    return {
      ...p,
      projection: snap.projection ?? p.projection,
      probability_over: snap.probability_over ?? p.probability_over,
      edge: snap.edge ?? p.edge,
      confidence: snap.confidence ?? p.confidence,
    };
  });
}
