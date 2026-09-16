import {calculate as combatCalculate} from './combat.js';
import {DropCalculator} from './drop.js';
export const CalculatorEngine=Object.freeze({
 combat:combatCalculate,
 drops:Object.freeze({probability:DropCalculator.probability,chanceAtLeastOne:DropCalculator.chanceAtLeastOne,chanceExactly:DropCalculator.chanceExactly,killsForChance:DropCalculator.killsForChance,expectedKills:DropCalculator.expectedKills,expectedTime:DropCalculator.expectedTime})
});
