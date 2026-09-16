import { Storage } from "./storage.js";
import { PlayerStore, PLAYER_KEY, DEFAULT_PLAYER } from "./player-store.js";

let migrated = false;
function migrateLegacyOnce() {
  if (migrated) return;
  migrated = true;
  if (Storage.jsonGet(PLAYER_KEY, null)) return;
  const player = structuredClone(DEFAULT_PLAYER);
  const skills = Storage.jsonGet("osrsProgress", {});
  if (skills && typeof skills === "object") player.skills = skills;
  const questProgress = Storage.jsonGet("osrsQuestProgress", {});
  if (questProgress && typeof questProgress === "object") {
    player.quests.completed = Object.entries(questProgress)
      .filter(([,v]) => v === true || v?.done === true).map(([k]) => k);
  }
  player.quests.questPoints = Number(Storage.get("osrsQuestPoints", "0")) || 0;
  const goals = Storage.jsonGet("osrsGoals", []);
  if (Array.isArray(goals)) player.goals = goals;
  if (player.skills || player.quests.completed.length || player.goals.length || player.quests.questPoints) PlayerStore.set(player);
}
export const loadPlayer = () => { migrateLegacyOnce(); return PlayerStore.get(); };
export const savePlayer = player => PlayerStore.set(player);
export const resetPlayer = () => PlayerStore.reset();
export const updateSkills = skills => PlayerStore.updateSkills(skills);
export const setSkill = (skill,current,target) => PlayerStore.setSkill(skill,current,target);
export const getSkill = skill => PlayerStore.getSkill(skill);
export const setQuestCompleted = (quest,completed=true) => PlayerStore.setQuestCompleted(quest,completed);
export const isQuestCompleted = quest => PlayerStore.isQuestCompleted(quest);
export const setQuestPoints = points => PlayerStore.setQuestPoints(points);
export const addGoal = goal => PlayerStore.addGoal(goal);
export const removeGoal = index => PlayerStore.removeGoal(index);
export const getGoals = () => PlayerStore.getGoals();
export const PlayerData = {loadPlayer,savePlayer,resetPlayer,updateSkills,setSkill,getSkill,setQuestCompleted,isQuestCompleted,setQuestPoints,addGoal,removeGoal,getGoals};
