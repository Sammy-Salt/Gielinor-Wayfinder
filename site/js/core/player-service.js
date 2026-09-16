import { PlayerStore } from "./player-store.js";
export const Player = Object.freeze({
  get: PlayerStore.get, save: PlayerStore.set, reset: PlayerStore.reset,
  getSkill: PlayerStore.getSkill, getSkills: PlayerStore.getSkills, setSkill: PlayerStore.setSkill,
  updateSkills: PlayerStore.updateSkills, isQuestCompleted: PlayerStore.isQuestCompleted,
  setQuestCompleted: PlayerStore.setQuestCompleted, setQuestPoints: PlayerStore.setQuestPoints,
  getGoals: PlayerStore.getGoals, addGoal: PlayerStore.addGoal, removeGoal: PlayerStore.removeGoal,
  subscribe: PlayerStore.subscribe
});
