import { debounce } from "../core/utils.js";
export function bindSearch(input, render, delay=150){ if(!input)return ()=>{}; const handler=debounce(render,delay); input.addEventListener("input",handler); return ()=>input.removeEventListener("input",handler); }
export function filterRecords(records,query,fields=["name"],limit=250){ const q=String(query||"").trim().toLowerCase(); const rows=q?records.filter(r=>fields.some(f=>String(r?.[f]??"").toLowerCase().includes(q))):records; return rows.slice(0,limit); }
