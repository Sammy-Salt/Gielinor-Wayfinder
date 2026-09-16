import {Storage} from "../core/storage.js";
import {Player} from "../core/player-service.js";
const KEY="progressTargets";
const clamp=v=>Math.max(1,Math.min(99,Number(v)||99));
export const ProgressService=Object.freeze({
 getTargets(){return Storage.jsonGet(KEY,{})||{}}, setTargets(targets){const clean={};for(const [k,v] of Object.entries(targets||{}))clean[String(k).toLowerCase()]=clamp(v);Storage.jsonSet(KEY,clean);return clean},
 getTarget(key,fallback=99){const v=this.getTargets()[String(key).toLowerCase()];return v==null?fallback:clamp(v)}, setTarget(key,value){const t=this.getTargets();t[String(key).toLowerCase()]=clamp(value);return this.setTargets(t)},clearTargets(){return this.setTargets({})},
 snapshot(){return {player:Player.get(),targets:this.getTargets()}}
});
