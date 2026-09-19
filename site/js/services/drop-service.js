import {CalculatorEngine} from '../calculators/engine.js';

function exactRate(record){
  const n=Number(record?.rateNumerator),d=Number(record?.rateDenominator);
  return Number.isFinite(n)&&Number.isFinite(d)&&n>0&&d>0&&!record?.rateApproximate&&
    (record?.rateStatus==='authoritative'||record?.rateStatus==='fallback');
}
function probability(record){
  if(!exactRate(record))return null;
  return Number(record.rateNumerator)/Number(record.rateDenominator);
}
function formatReciprocal(n,d){
  n=Number(n); d=Number(d);
  if(!Number.isFinite(n)||!Number.isFinite(d)||n<=0||d<=0)return null;
  const reciprocal=d/n;
  if(!Number.isFinite(reciprocal)||reciprocal<=0)return null;
  const rounded=Math.round((reciprocal+Number.EPSILON)*100)/100;
  return `1/${Number.isInteger(rounded)?rounded:rounded.toFixed(2).replace(/0+$/,'').replace(/\.$/,'')}`;
}
function display(record){
  if(!exactRate(record))return null;
  return formatReciprocal(record.rateNumerator,record.rateDenominator)||record.rateDisplay||null;
}
function label(record){
  if(exactRate(record)){
    const shown=display(record)||'Rate unavailable';
    const source=record.rateSource||'source';
    return `${shown} (${source})`;
  }
  if(record?.rateStatus==='conflict')return 'Rate unresolved';
  return 'Rate unavailable';
}
export const Drops=Object.freeze({
  ...CalculatorEngine.drops,
  isExactRate:exactRate,
  probability,
  formatReciprocal,
  rateDisplay:display,
  rateLabel:label
});
