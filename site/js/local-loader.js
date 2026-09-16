(async function(){
  const isLocal=['localhost','127.0.0.1'].includes(location.hostname);

  function showStartupError(error){
    const main=document.querySelector('main,.osrs-content,.container,.content');
    if(!main)return;
    const card=document.createElement('div');
    card.className='card';
    const h=document.createElement('h2');
    h.textContent='Unable to start OSRS Guide';
    const p=document.createElement('p');
    p.textContent=String(error?.message||error);
    card.append(h,p);
    main.replaceChildren(card);
  }

  async function clearLocalRuntime(){
    if(!isLocal || !('serviceWorker' in navigator))return false;
    const controlled=Boolean(navigator.serviceWorker.controller);
    try{
      const regs=await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map(r=>r.unregister()));
      if('caches' in window){
        const keys=await caches.keys();
        await Promise.all(keys.map(k=>caches.delete(k)));
      }
    }catch(e){ console.warn('[OSRS Guide] localhost cache cleanup:',e); }
    return controlled;
  }

  async function refreshWorkerBeforeBootstrap(){
    if(isLocal || !('serviceWorker' in navigator))return;
    try{
      const reg=await navigator.serviceWorker.getRegistration('./');
      if(!reg)return;
      const previous=reg.active;
      await reg.update();
      if(reg.waiting){
        reg.waiting.postMessage({type:"SKIP_WAITING"});
      }
      if(reg.installing || reg.waiting){
        await new Promise(resolve=>{
          let done=false;
          const finish=()=>{if(done)return;done=true;clearTimeout(timer);navigator.serviceWorker.removeEventListener('controllerchange',finish);resolve();};
          const timer=setTimeout(finish,4000);
          navigator.serviceWorker.addEventListener('controllerchange',finish);
          const watch=()=>{if(reg.active && reg.active!==previous)finish();};
          reg.addEventListener('updatefound',watch,{once:true});
          watch();
        });
      }
    }catch(e){ console.warn('[OSRS Guide] service worker refresh:',e); }
  }

  try{
    if(await clearLocalRuntime()){
      location.reload();
      return;
    }
    await refreshWorkerBeforeBootstrap();
    const release=await fetch('./release.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(`release.json HTTP ${r.status}`);return r.json();});
    const loaderVersion=String(release.loaderVersion||'');
    if(!/^\d+$/.test(loaderVersion))throw new Error('Invalid release loaderVersion');
    await import(`./bootstrap.js?v=${encodeURIComponent(loaderVersion)}`);
  }catch(error){
    console.error('[OSRS Guide] bootstrap failed',error);
    showStartupError(error);
  }
})();
