import {Quests} from '../core/quest-service.js';
import {OSRSQuestEngine} from './dependency-engine.js';
import {Progression} from './progression-service.js';
export async function snapshot(){const progress=Progression.snapshot();await Quests.load();const quests=Quests.all();const ready=quests.filter(q=>OSRSQuestEngine.checkQuest(q).ready);const blocked=quests.filter(q=>!OSRSQuestEngine.checkQuest(q).ready&&!OSRSQuestEngine.checkQuest(q).completed);return {progress,ready:ready.slice(0,6),blockedCount:blocked.length,questCount:quests.length};}
export const Assistant=Object.freeze({snapshot});
