const values = new Map();
const subscribers = new Map();
function clone(v){ return v && typeof v === "object" ? structuredClone(v) : v; }
export const State = Object.freeze({
  get(key, fallback=null){ return values.has(key) ? clone(values.get(key)) : fallback; },
  set(key, value){ values.set(key, clone(value)); for(const fn of subscribers.get(key)||[]) fn(clone(value)); return clone(value); },
  update(key, updater){ return State.set(key, updater(State.get(key))); },
  subscribe(key, fn){ if(!subscribers.has(key)) subscribers.set(key,new Set()); subscribers.get(key).add(fn); return ()=>subscribers.get(key)?.delete(fn); },
  clear(key){ if(key) values.delete(key); else values.clear(); }
});
