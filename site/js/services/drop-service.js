import {CalculatorEngine} from '../calculators/engine.js';

function exactRate(record){
  const n=Number(record?.rateNumerator),d=Number(record?.rateDenominator);
  return Number.isFinite(n)&&Number.isFinite(d)&&n>0&&d>0&&!record?.rateApproximate&&record?.rateStatus==='fallback';
}
function probability(record){
  if(!exactRate(record)) return null;
  return Number(record.rateNumerator)/Number(record.rateDenominator);
}
function label(record){
  if(exactRate(record)) return `${record.rateDisplay||`${record.rateNumerator}/${record.rateDenominator}`} (${record.rateSource||'secondary'})`;
  if(record?.rateStatus==='conflict') return 'Rate unresolved';
  return 'Rate unavailable';
}
export const Drops=Object.freeze({
  ...CalculatorEngine.drops,
  isExactRate:exactRate,
  probability,
  rateLabel:label
});
