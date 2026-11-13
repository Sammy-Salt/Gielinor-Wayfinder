import {Events} from './events.js';
import {Logger} from './logger.js';
export async function initPlatform(){
 if(document.body.dataset.page==='map')return;
 // Local Termux testing must never install/control a PWA service worker.
 // The service worker is intentionally reserved for real deployed origins.
 if('serviceWorker' in navigator && !['localhost','127.0.0.1'].includes(location.hostname)){
  try{await navigator.serviceWorker.register('./sw.js',{scope:'./'});}catch(e){Logger.warn('Service worker unavailable',e)}
 }
 const state=document.getElementById('offlineStatus');
 if(state){const update=()=>{state.textContent=navigator.onLine?'Online · offline cache ready':'Offline mode';};addEventListener('online',update);addEventListener('offline',update);update();}
 Events.emit('platform:ready',{serviceWorker:'serviceWorker' in navigator && !['localhost','127.0.0.1'].includes(location.hostname),indexedDB:'indexedDB' in globalThis});
}
export const Platform=Object.freeze({init:initPlatform});
