import {Quests} from '../core/quest-service.js';
import {OSRSQuestEngine} from './dependency-engine.js';
export const Planner=Object.freeze({
 async quest(name){await Quests.load();const q=Quests.byName(name)||Quests.search(name,1)[0];if(!q)return null;return OSRSQuestEngine.buildPlan(q.name);},
 async readyQuests(){await Quests.load();return Quests.all().filter(q=>OSRSQuestEngine.checkQuest(q).ready);},
 async missingForQuest(name){const p=await this.quest(name);return p?{skills:p.skills,quests:p.quests,questPoints:p.questPoints}:null}
});
