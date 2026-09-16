import {parseDropRate} from '../core/utils.js';
import {CalculatorEngine} from '../calculators/engine.js';
export const Drops=Object.freeze({parseRate:parseDropRate,...CalculatorEngine.drops});
