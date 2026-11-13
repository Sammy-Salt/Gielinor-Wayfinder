/* Light/dark theme. Dark is the default; with no saved choice the system setting decides (see site.css).
 * Runs in <head> so the saved choice is applied before first paint. */
(function(){
  var KEY="wayfinder.theme",root=document.documentElement;
  function saved(){try{var v=localStorage.getItem(KEY);return v==="light"||v==="dark"?v:null;}catch(e){return null;}}
  function current(){var s=saved();if(s)return s;return window.matchMedia&&window.matchMedia("(prefers-color-scheme: light)").matches?"light":"dark";}
  function apply(t){root.setAttribute("data-theme",t);var m=document.querySelectorAll('meta[name="theme-color"]');for(var i=0;i<m.length;i++)m[i].setAttribute("content",t==="light"?"#f7f7f5":"#111111");}
  if(saved())apply(saved());
  document.addEventListener("DOMContentLoaded",function(){
    var nav=document.getElementById("site-nav");if(!nav||nav.querySelector(".theme-toggle"))return;
    var b=document.createElement("button");b.type="button";b.className="theme-toggle";
    b.innerHTML='<svg class="icon-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/></svg><svg class="icon-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4 8 8 0 1 0 20 14.5z"/></svg>';
    function label(){b.setAttribute("aria-label",current()==="light"?"Switch to dark mode":"Switch to light mode");}
    b.addEventListener("click",function(){var next=current()==="light"?"dark":"light";apply(next);try{localStorage.setItem(KEY,next);}catch(e){}label();});
    label();nav.appendChild(b);
  });
})();
