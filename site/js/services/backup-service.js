import {Player} from '../core/player-service.js';
import {ProgressService} from './progress-service.js';
const VERSION=1;
export const Backup=Object.freeze({
 export(){return {formatVersion:VERSION,app:'Gielinor Wayfinder',createdAt:new Date().toISOString(),player:Player.get(),progressTargets:ProgressService.getTargets()}},
 import(snapshot){if(!snapshot||snapshot.formatVersion!==VERSION||!snapshot.player)throw new Error('Invalid Gielinor Wayfinder backup');Player.save(snapshot.player);if(snapshot.progressTargets)ProgressService.setTargets(snapshot.progressTargets);return true}
});
