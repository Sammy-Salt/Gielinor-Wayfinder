import { parseDropRate } from "../core/utils.js";
export function probability(rate){ const p=parseDropRate(rate); return p==null?0:1/p; }
export function chance(rate){ const p=parseDropRate(rate); return p==null?0:1/p; }
export function expectedKills(rate){ const d=parseDropRate(rate); return d==null?Infinity:d; }
