import {Player} from '../core/player-service.js';
import {ProgressService} from './progress-service.js';
export const SKILLS=Object.freeze([
 ['Attack','Attack'],['Strength','Strength'],['Defence','Defence'],['Ranged','Range'],['Prayer','Prayer'],['Magic','Magic'],['Runecraft','Runecrafting'],['Construction','Construction'],['Hitpoints','Hitpoints'],['Agility','Agility'],['Herblore','Herblore'],['Thieving','Thieving'],['Crafting','Crafting'],['Fletching','Fletching'],['Slayer','Slayer'],['Hunter','Hunter'],['Mining','Mining'],['Smithing','Smithing'],['Fishing','Fishing'],['Cooking','Cooking'],['Firemaking','Firemaking'],['Woodcutting','Woodcutting'],['Farming','Farming'],['Summoning','Summoning']
]);
const XP=[];let points=0;for(let level=1;level<=99;level++){XP[level]=Math.floor(points/4);points+=Math.floor(level+300*Math.pow(2,level/7));}
const aliases={ranged:'Range',runecrafting:'Runecrafting',runecraft:'Runecrafting'};
function xpForLevel(level){return XP[Math.max(1,Math.min(99,Number(level)||1))]||0;}
function get(skill){const s=Player.getSkill(skill[1])||Player.getSkill(skill[0]);const level=Math.max(1,Math.min(99,Number(s?.current??s?.level??1)));const xp=Math.max(0,Number(s?.xp)||0);return {level,xp,target:ProgressService.getTarget(skill[1],99)};}
export const Progression=Object.freeze({xpForLevel,get,normalizeSkill(name){const n=String(name||'').trim().toLowerCase();return aliases[n]||name;},snapshot(){let totalLevel=0,totalXP=0,targetsMet=0,progress=0;const skills=SKILLS.map(([display,lookup])=>{const x=get([display,lookup]);totalLevel+=x.level;totalXP+=x.xp;if(x.level>=x.target)targetsMet++;const p=x.target<=1?1:Math.max(0,Math.min(1,(x.level-1)/(x.target-1)));progress+=p;return {...x,display,lookup};});return {skills,totalLevel,totalXP,targetsMet,skillCount:skills.length,overall:skills.length?progress/skills.length*100:0,questPoints:Number(Player.get()?.quests?.questPoints||0),playerName:Player.get()?.name||'Player'};}});
