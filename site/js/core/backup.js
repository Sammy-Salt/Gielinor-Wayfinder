import { PlayerStore } from "./player-store.js";
const NAME="gielinor-wayfinder-player-v4.json";
export function exportPlayer(){const blob=new Blob([JSON.stringify({formatVersion:4,exportedAt:new Date().toISOString(),player:PlayerStore.get()},null,2)],{type:"application/json"});const url=URL.createObjectURL(blob);const a=document.createElement("a");a.href=url;a.download=NAME;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
export async function importPlayer(file){const text=await file.text();const payload=JSON.parse(text);const player=payload?.player||payload;if(!player||typeof player!=="object")throw new Error("Invalid player backup");PlayerStore.set(player);return PlayerStore.get();}
export const PlayerBackup=Object.freeze({export:exportPlayer,import:importPlayer});
