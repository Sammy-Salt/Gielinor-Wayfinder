import {Events} from './events.js';
import {Logger} from './logger.js';
export async function initPlatform(){
 if(document.body.dataset.page==='map')return;
 // Inside the Android app every file is bundled in the APK: no service worker, no install prompt, no connection status.
 const native=Boolean(globalThis.Capacitor?.isNativePlatform?.());
 // Local Termux testing must never install/control a PWA service worker.
 // The service worker is intentionally reserved for real deployed origins.
 if(!native && 'serviceWorker' in navigator && !['localhost','127.0.0.1'].includes(location.hostname)){
  try{await navigator.serviceWorker.register('./sw.js',{scope:'./'});}catch(e){Logger.warn('Service worker unavailable',e)}
 }
 const state=document.getElementById('offlineStatus');
 if(state && native){state.textContent='Offline app';}
 else if(state){const update=()=>{state.textContent=navigator.onLine?'Online · offline cache ready':'Offline mode';};addEventListener('online',update);addEventListener('offline',update);update();}
 Events.emit('platform:ready',{native,serviceWorker:!native && 'serviceWorker' in navigator && !['localhost','127.0.0.1'].includes(location.hostname),indexedDB:'indexedDB' in globalThis});
}
export const Platform=Object.freeze({init:initPlatform});
