const BUILD_ID='pass31.48-20261108-1';
const CACHE_NAMESPACE='gielinor-wayfinder-pass31.48-20261108-1';
const CACHE=CACHE_NAMESPACE;
const SHELL=["./","./index.html","./data/recipes.json","./css/pages/crafting.css","./css/pages/character.css","./js/pages/crafting.js","./js/pages/character.js","./crafting.html","./character.html","./offline.html","./site.css","./manifest.webmanifest","./icon.svg","./icons/icon.svg","./icons/icon-192.png","./icons/icon-512.png",
"./boss.html","./bosses.html","./calculators.html","./combat-stats.html","./drop-stats.html","./drop-time.html","./goals.html","./item.html","./items.html","./monster.html","./monsters.html","./npc.html","./npcs.html","./progress.html","./quest.html","./quests.html","./skill-stats.html",
"./css/pages/boss.css","./css/pages/bosses.css","./css/pages/calculators.css","./css/pages/combat-stats.css","./css/pages/drop-stats.css","./css/pages/drop-time.css","./css/pages/goals.css","./css/pages/index.css","./css/pages/item.css","./css/pages/items.css","./css/pages/map.css","./css/pages/monster.css","./css/pages/monsters.css","./css/pages/npc.css","./css/pages/npcs.css","./css/pages/progress.css","./css/pages/quests.css","./css/pages/skill-stats.css","./data/player-sync.json","./data/quests.json","./data/items/index.json","./data/monsters/index.json","./data/monsters/display-index.json","./data/npcs/index.json","./data/knowledge/index.json","./data/relationships/index.json","./data/sources/2009scape/drop_tables.json","./data/sources/2009scape/drop_tables.manifest.json","./data/catalog-manifest.json","./data/wiki/pass31.13/manifest.json","./data/wiki/pass31.13/summary.json","./data/wiki/pass31.13/entities/items/index.json","./data/wiki/pass31.13/entities/monsters/index.json","./data/wiki/pass31.13/entities/equipment/index.json","./data/wiki/pass31.13/relationships/drops.json","./data/wiki/pass31.13/relationships/recipes.json","./js/local-loader.js?v=42","./js/bootstrap.js?v=42","./js/core/shell.js?v=42","./js/components/app-enhancer.js?v=42","./js/pages/item.js?v=42","./release.json"];

self.addEventListener('message',event=>{
  if(event.data?.type==='SKIP_WAITING') self.skipWaiting();
});

self.addEventListener('install',event=>{
  event.waitUntil(
    caches.open(CACHE)
      .then(async cache=>{
        const failures=[];
        for(const url of SHELL){
          try{
            const response=await fetch(url,{cache:'no-store'});
            if(!response.ok)throw new Error(`HTTP ${response.status}`);
            await cache.put(url,response.clone());
          }catch(error){
            failures.push(`${url}: ${error?.message||error}`);
          }
        }
        if(failures.length)throw new Error(`Offline shell installation failed (${failures.length}): ${failures.join('; ')}`);
      })
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate',event=>{
  event.waitUntil(
    caches.keys()
      .then(keys=>Promise.all(keys.filter(key=>key!==CACHE).map(key=>caches.delete(key))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',event=>{
  const request=event.request;
  if(request.method!=='GET'||new URL(request.url).origin!==location.origin)return;

  if(request.mode==='navigate'){
    event.respondWith(
      fetch(request,{cache:'no-store'})
        .then(response=>{
          const copy=response.clone();
          caches.open(CACHE).then(cache=>cache.put(request,copy));
          return response;
        })
        .catch(()=>caches.match(request).then(cached=>cached||caches.match('./offline.html')))
    );
    return;
  }

  const pathname=new URL(request.url).pathname;
  const isAppCode=/\.(?:js|css)$/.test(pathname);
  if(isAppCode){
    event.respondWith(
      fetch(request,{cache:'no-store'})
        .then(response=>{
          if(response.ok)caches.open(CACHE).then(cache=>cache.put(request,response.clone()));
          return response;
        })
        .catch(()=>caches.match(request))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached=>{
      const network=fetch(request).then(response=>{
        if(response.ok)caches.open(CACHE).then(cache=>cache.put(request,response.clone()));
        return response;
      }).catch(()=>cached);
      return cached||network;
    })
  );
});
