export function probability(rate){const r=Number(rate);return Number.isFinite(r)&&r>0?1/r:null;}
export function chanceAtLeastOne(rate,kills){const p=probability(rate),n=Math.max(0,Number(kills)||0);return p==null?null:1-Math.pow(1-p,n);}
export function chanceExactly(rate,kills,count=1){const p=probability(rate),n=Math.max(0,Math.floor(Number(kills)||0)),k=Math.floor(Number(count)||0);if(p==null||k<0||k>n)return 0;let c=1;for(let i=1;i<=k;i++)c*=((n-k+i)/i);return c*Math.pow(p,k)*Math.pow(1-p,n-k);}
export function killsForChance(rate,chance){const p=probability(rate),c=Number(chance);if(p==null||!(c>0&&c<1))return c>=1?Infinity:0;return Math.ceil(Math.log(1-c)/Math.log(1-p));}
export function expectedKills(rate){const r=Number(rate);return Number.isFinite(r)&&r>0?r:null;}
export function expectedTime(rate,kph){const r=expectedKills(rate),k=Number(kph);return r!=null&&k>0?r/k*3600:null;}
export const DropCalculator=Object.freeze({probability,chanceAtLeastOne,chanceExactly,killsForChance,expectedKills,expectedTime});
