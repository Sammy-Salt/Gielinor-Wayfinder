const topics=new Map();
export const Events=Object.freeze({
 on(topic,fn){if(!topics.has(topic))topics.set(topic,new Set());topics.get(topic).add(fn);return()=>topics.get(topic)?.delete(fn);},
 emit(topic,payload){for(const fn of topics.get(topic)||[])try{fn(payload)}catch(e){console.error(`[OSRS Guide] event ${topic}`,e)}},
 clear(topic){if(topic)topics.delete(topic);else topics.clear();}
});
