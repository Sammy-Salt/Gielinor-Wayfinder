const routes=new Map();
const normalizePath=value=>{const raw=String(value||"").split("?")[0].split("#")[0];const name=raw.split("/").filter(Boolean).pop()||"index.html";return name.toLowerCase().endsWith(".html")?name.toLowerCase():`${name.toLowerCase()}.html`;};
export const Router=Object.freeze({
 register(path,loader){routes.set(normalizePath(path),loader);return Router;},
 resolve(location=globalThis.location){return routes.get(normalizePath(location?.pathname));},
 current(){return normalizePath(globalThis.location);},
 params(location=globalThis.location){return new URLSearchParams(location?.search||"");},
 href(path,params={}){const q=new URLSearchParams(params);return `${normalizePath(path)}${q.toString()?`?${q}`:""}`;},
 isKnown(path){return routes.has(normalizePath(path));},
 async navigate(url,{replace=false}={}){const target=String(url);if(replace)history.replaceState({},"",target);else history.pushState({},"",target);globalThis.dispatchEvent(new PopStateEvent("popstate"));return target;},
 onChange(fn){const handler=()=>fn(Router.current(),Router.params());addEventListener("popstate",handler);return()=>removeEventListener("popstate",handler);},
 routes:()=>[...routes.keys()]
});
