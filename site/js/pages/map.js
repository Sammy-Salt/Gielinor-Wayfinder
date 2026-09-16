const locations =
    window.OSRS_MAP_LOCATIONS || [];

/*
 * OSRS map tiles.
 *
 * Explv's public tile layout:
 *
 * plane/{z}/{x}/{y}.png
 */

const ZOOM = 7;

function tileCenter(x, y) {
    const pixelX = (x + 0.5) * 256;
    const pixelY = (y + 0.5) * 256;

    return [
        -pixelY / Math.pow(2, ZOOM),
        pixelX / Math.pow(2, ZOOM)
    ];
}

let currentPlane = 0;

function planeMaxZoom(plane){
    return Number(plane) === 0 ? 8 : 8;
}

const map = L.map("map",{
    minZoom:4,
    maxZoom:11,
    zoomControl:true,
    attributionControl:true
});

/*
 * The original OSRS tile system uses TMS numbering.
 */
let tileLayer =
    L.tileLayer(
        `data/map/assets/${currentPlane}/{z}/{x}/{y}.png`,
        {
            minZoom:4,
            maxZoom:planeMaxZoom(currentPlane),
            tms:true,
            tileSize:256,
            noWrap:true,
            keepBuffer:2,
            updateWhenIdle:true,
            updateWhenZooming:false,
            attribution:"OSRS map tiles © Explv"
        }
    ).addTo(map);

map.setMaxZoom(planeMaxZoom(currentPlane));
map.setView([-79,-137], 7);

/*
 * Coordinate display.
 */

const coordinateControl =
    L.control({
        position:"bottomright"
    });

coordinateControl.onAdd =
    function(){

        const div =
            L.DomUtil.create(
                "div",
                "coord-box"
            );

        div.textContent =
            "X: — | Y: — | Plane: 0";

        return div;
    };

coordinateControl.addTo(map);

const coordinateElement =
    coordinateControl
        .getContainer();

/*
 * Convert Leaflet map coordinates into
 * approximate OSRS world coordinates.
 *
 * This is kept isolated so we can replace
 * it with exact RuneLite/world-point math
 * later without changing the rest of
 * the map.
 */

function osrsToLatLng(x, y){
    const MAP_HEIGHT_MAX_ZOOM_PX = 364544;
    const RS_TILE_WIDTH_PX = 32;
    const RS_TILE_HEIGHT_PX = 32;
    const RS_OFFSET_X = 960;
    const RS_OFFSET_Y = 6208;

    const px =
        ((Number(x) - RS_OFFSET_X) * RS_TILE_WIDTH_PX) +
        (RS_TILE_WIDTH_PX / 4);

    const py =
        MAP_HEIGHT_MAX_ZOOM_PX -
        ((Number(y) - RS_OFFSET_Y) * RS_TILE_HEIGHT_PX);

    return map.unproject(
        L.point(px, py),
        map.getMaxZoom()
    );
}

function addCoordinateTestPin(latlng){
    const coords = mapToOSRS(latlng);

    if(window.coordinateTestPin){
        map.removeLayer(window.coordinateTestPin);
    }

    window.coordinateTestPin = L.marker(latlng,{
        icon:L.divIcon({
            className:"coordinate-test-pin",
            html:"📍",
            iconSize:[30,30],
            iconAnchor:[15,30]
        })
    }).addTo(map);

    const info=document.getElementById("info");
    info.style.display="block";
    info.innerHTML=
        "<h2>📍 Test Pin</h2>"+
        "<p><b>OSRS X:</b> "+coords.x+"</p>"+
        "<p><b>OSRS Y:</b> "+coords.y+"</p>"+
        "<p><b>Plane:</b> "+currentPlane+"</p>";
}

map.on("click",function(e){
    addCoordinateTestPin(e.latlng);
});

function mapToOSRS(latlng){
    const point = map.project(latlng, 11);

    const x =
        Math.round(
            ((point.x - 8) / 32) + 960
        );

    const y =
        Math.round(
            ((364544 - point.y) / 32) + 6208
        );

    return {x:x, y:y};
}

/*
 * Update coordinates while moving.
 */

let coordinateFrame = 0;
let pendingLatLng = null;

map.on("mousemove", function(event){
    pendingLatLng = event.latlng;
    if (coordinateFrame) return;

    coordinateFrame = requestAnimationFrame(function(){
        coordinateFrame = 0;
        if (!pendingLatLng) return;
        const p = mapToOSRS(pendingLatLng);
        coordinateElement.textContent =
            `X: ${p.x} | Y: ${p.y} | Plane: ${currentPlane}`;
    });
});

map.on(
    "click",
    function(event){

        const p =
            mapToOSRS(event.latlng);

        coordinateElement.textContent =
            `X: ${p.x} | Y: ${p.y} | Plane: ${currentPlane}`;
    }
);

/*
 * Location marker layer.
 */

const markerLayer =
    L.layerGroup().addTo(map);

const npcLayer =
    L.layerGroup().addTo(map);

const shopLayer =
    L.layerGroup().addTo(map);

const npcs =
    window.OSRS_MAP_NPCS || [];

const shops =
    window.OSRS_MAP_SHOPS || [];

const markerIcons = {
    NPC: L.divIcon({
        className:"map-marker",
        html:"<span>👤</span>",
        iconSize:[28,28],
        iconAnchor:[14,14]
    }),
    Shop: L.divIcon({
        className:"map-marker",
        html:"<span>🏪</span>",
        iconSize:[28,28],
        iconAnchor:[14,14]
    })
};

function markerIcon(type){
    return markerIcons[type === "Shop" ? "Shop" : "NPC"];
}

const locationByPlane = new Map();
const npcByPlane = new Map();
const shopByPlane = new Map();

function indexByPlane(items, target){
    for (const item of items) {
        const plane = item.plane === undefined ? 0 : Number(item.plane);
        let list = target.get(plane);
        if (!list) {
            list = [];
            target.set(plane, list);
        }
        list.push(item);
    }
}

indexByPlane(locations, locationByPlane);
indexByPlane(npcs, npcByPlane);
indexByPlane(shops, shopByPlane);

function planeItems(index, plane){
    return index.get(Number(plane)) || [];
}

function addInteractiveMarkers(){

    npcLayer.clearLayers();
    shopLayer.clearLayers();

    planeItems(npcByPlane, currentPlane).forEach(function(npc){

        const target =
            osrsToLatLng(npc.x,npc.y);

        const marker =
            L.marker(
                [target.lat,target.lng],
                {
                    icon:markerIcon("NPC")
                }
            );

        marker.on("click",function(){

            showLocation({
                name:npc.name,
                description:npc.description ||
                    npc.examine || "NPC",
                category:"NPC",
                x:npc.x,
                y:npc.y,
                plane:npc.plane ?? 0
            });

        });

        npcLayer.addLayer(marker);
    });

    planeItems(shopByPlane, currentPlane).forEach(function(shop){

        const target =
            osrsToLatLng(shop.x,shop.y);

        const marker =
            L.marker(
                [target.lat,target.lng],
                {
                    icon:markerIcon("Shop")
                }
            );

        marker.on("click",function(){

            showLocation({
                name:shop.name,
                description:
                    shop.description ||
                    shop.type ||
                    "Shop",
                category:"Shop",
                x:shop.x,
                y:shop.y,
                plane:shop.plane ?? 0
            });

        });

        shopLayer.addLayer(marker);
    });
}

function addLocations(){

    markerLayer.clearLayers();

    addInteractiveMarkers();

    planeItems(locationByPlane, currentPlane).forEach(function(loc){

        const target = osrsToLatLng(
            loc.x,
            loc.y
        );

        const marker = L.marker(
            [target.lat, target.lng],
            {
                interactive:false,
                icon:L.divIcon({
                    className:"town-label",
                    html:"<span>" + loc.name + "</span>",
                    iconSize:null
                })
            }
        );

        markerLayer.addLayer(marker);
    });
}function locationColor(category){

    switch(category){

        case "bank":
            return "#55a7ff";

        case "quest":
            return "#e6d34d";

        case "transport":
            return "#a86cff";

        case "resource":
            return "#55c96f";

        case "npc":
            return "#ff704d";

        case "entrance":
            return "#aaa";

        case "city":
            return "#d6a84f";

        default:
            return "#fff";
    }
}

/*
 * Location information panel.
 */

function showLocation(loc){

    const info =
        document.getElementById("info");

    info.style.display =
        "block";

    info.innerHTML = `
        <h2>${escapeHtml(loc.name)}</h2>

        <p>
            ${escapeHtml(
                loc.description || ""
            )}
        </p>

        <p>
            <b>Category:</b>
            ${escapeHtml(
                loc.category || "location"
            )}
        </p>

        <p>
            <b>X:</b> ${loc.x}
            &nbsp;
            <b>Y:</b> ${loc.y}
            &nbsp;
            <b>Plane:</b>
            ${loc.plane ?? 0}
        </p>
    `;
}


/*
 * Search.
 */

const search =
    document.getElementById("search");

const results =
    document.getElementById("results");

search.addEventListener(
    "input",
    function(){

        const q =
            search.value
                .trim()
                .toLowerCase();

        if(!q){

            results.style.display =
                "none";

            results.innerHTML =
                "";

            return;
        }

        const found =
            locations
                .filter(
                    loc =>
                        loc.name
                            .toLowerCase()
                            .includes(q) ||
                        (
                            loc.description || ""
                        )
                            .toLowerCase()
                            .includes(q)
                )
                .slice(0,30);

        results.innerHTML =
            "";

        found.forEach(
            function(loc){

                const row =
                    document.createElement("button");

                row.type = "button";

                row.className =
                    "result";

                row.replaceChildren();
                const title = document.createElement("b");
                title.textContent = loc.name || "Unnamed location";
                const coords = document.createElement("small");
                coords.textContent = `${loc.x}, ${loc.y}`;
                row.append(title, coords);

                row.onclick =
                    function(){

                        const target =
                            osrsToLatLng(
                                loc.x,
                                loc.y
                            );

                        const lat = target.lat;
                        const lng = target.lng;

                        if(
                            loc.plane !== undefined &&
                            Number(loc.plane) !== currentPlane
                        ){
                            currentPlane = Number(loc.plane);
                            document.getElementById("plane").value =
                                currentPlane;

                            map.setMaxZoom(
                                planeMaxZoom(currentPlane)
                            );

                            map.removeLayer(tileLayer);

                            tileLayer = L.tileLayer(
                                `data/map/assets/${currentPlane}/{z}/{x}/{y}.png`,
                                {
                                    minZoom:4,
                                    maxZoom:planeMaxZoom(currentPlane),
                                    tms:true,
                                    tileSize:256,
                                    noWrap:true,
                                    attribution:"OSRS map tiles © Explv"
                                }
                            ).addTo(map);

                            addLocations();
                        }

                        map.setView(
                            [lat,lng],
                            Math.min(9, planeMaxZoom(currentPlane))
                        );

                        showLocation(loc);

                        results.style.display =
                            "none";

                        search.value =
                            loc.name;
                    };

                results.appendChild(row);
            }
        );

        results.style.display =
            found.length
                ? "block"
                : "none";
    }
);

/*
 * Plane switching.
 */

document
    .getElementById("plane")
    .addEventListener(
        "change",
        function(){

            currentPlane =
                Number(this.value);

            map.setMaxZoom(
                planeMaxZoom(currentPlane)
            );

            if(map.getZoom() > planeMaxZoom(currentPlane)){
                map.setZoom(planeMaxZoom(currentPlane));
            }

            map.removeLayer(
                tileLayer
            );

            tileLayer =
                L.tileLayer(
                    `data/map/assets/${currentPlane}/{z}/{x}/{y}.png`,
                    {
                        minZoom:4,
                        maxZoom:planeMaxZoom(currentPlane),
                        tms:true,
                        tileSize:256,
                        noWrap:true,
                        attribution:
                            "OSRS map tiles © Explv"
                    }
                )
                .addTo(map);

            addLocations();

        }
    );

addLocations();


/* Interactive OSRS-style legend */
const legendCategories = {
 "Main / World Map":[
  "Agility shortcut","Altar","Bank","Clan Hub","Combat Achievements",
  "Death's Office","Distraction and Diversion","Docking point","Dungeon",
  "Dungeon with map link","Hairdresser","Holiday event","House portal",
  "Makeover mage","Map link","Minigame","Poll booth","Quest start",
  "Raid","Task Master","Transportation"
 ],
 "Tutors":[
  "Bank tutor","Bond tutor","Clue tutor","Combat tutor","Cooking tutor",
  "Crafting tutor","Danger tutor","Deadman tutor","Fishing tutor",
  "Hunting tutor","Ironman tutor","Leagues tutor","Lumbridge Guide",
  "Mining tutor","Prayer tutor","Security tutor","Smithing tutor",
  "Woodcutting tutor"
 ],
 "Training":[
  "Agility training","Anvil","Bird house trapping sites","Brewery",
  "Combat training","Cooking range","Dairy churn","Dairy cow",
  "Farming patch","Fishing spot","Furnace site","Hunter training",
  "Loom","Mining site","Potters wheel","Rare trees","Sand pit",
  "Slayer Master","Spinning wheel","Thieving activity","Trip hammer",
  "Water source","Windmill","Woodcutting stump"
 ],
 "Shopping":[
  "Amulet shop","Archery shop","Axe shop","Bar","Candle shop",
  "Clothes shop","Crafting shop","Dye shop","Farming shop",
  "Fishing shop","Food shop","Fur trader","Gem shop","General store",
  "Helmet shop","Herblore shop","Hunter shop","Jewellery shop",
  "Kebab seller","Mace shop","Magic shop","Mining shop","Other",
  "Platebody shop","Platelegs shop","Plateskirt shop","Rewards shop",
  "Scimitar shop","Shield shop","Silk shop","Silver shop","Spice shop",
  "Staff shop","Sword shop","Vegetable shop","Wine shop"
 ]
};

const legendLayer=L.layerGroup().addTo(map);

function getShopData(){return window.OSRS_MAP_SHOPS||[];}

function legendMatches(loc,category){
 const c=category.toLowerCase();

 if(loc.shopType)
  return String(loc.shopType).toLowerCase()===c;

 const text=(
  (loc.name||"")+" "+
  (loc.description||"")+" "+
  (loc.type||"")
 ).toLowerCase();

 return text.includes(c);
}

function showLegendCategory(category){
 legendLayer.clearLayers();

 let source=locations;

 // Shopping categories come from shops.js.
 if(legendCategories.Shopping.includes(category)){
  source=getShopData();
 }

 const found=source.filter(loc=>{
  if(loc.plane!==undefined &&
     Number(loc.plane)!==currentPlane) return false;

  return legendMatches(loc,category);
 });

 found.forEach(loc=>{
  const target=osrsToLatLng(loc.x,loc.y);

  const marker=L.circleMarker(
   [target.lat,target.lng],
   {
    radius:7,
    color:"#ff0000",
    fillColor:"#ff0000",
    fillOpacity:1,
    weight:2
   }
  );

  let info="<b>"+escapeHtml(loc.name||category)+"</b>";

  if(loc.location)
   info+="<br>📍 "+escapeHtml(loc.location);

  if(loc.shopType)
   info+="<br>🛒 "+escapeHtml(loc.shopType);

  if(loc.owner)
   info+="<br>Owner: "+escapeHtml(
    String(loc.owner).replace(/\[\[|\]\]/g,"")
   );

  if(loc.description)
   info+="<br><br>"+escapeHtml(loc.description);

  marker.bindPopup(info);
  legendLayer.addLayer(marker);
 });

 if(found.length){
  const bounds=L.latLngBounds(
   found.map(loc=>{
    const p=osrsToLatLng(loc.x,loc.y);
    return [p.lat,p.lng];
   })
  );

  map.fitBounds(bounds,{
   padding:[60,60],
   maxZoom:9
  });
 }

 document.getElementById("info").innerHTML=
  "<b>"+escapeHtml(category)+"</b><br>"+
  found.length+" location(s) found.<br>"+
  "Data: "+source.length+" entries";
}

function buildLegend(){
 const content=document.getElementById("legendContent");
 content.innerHTML="";

 Object.entries(legendCategories).forEach(([section,items])=>{
  const wrap=document.createElement("div");
  wrap.className="legendSection";

  const title=document.createElement("button");
  title.type="button";
  title.className="legendTitle";
  title.textContent=section+" ▸";

  const list=document.createElement("div");
  list.className="legendItems";

  title.addEventListener("click",()=>{
   const open=list.style.display==="block";
   list.style.display=open?"none":"block";
   title.setAttribute("aria-expanded",String(!open));
   title.textContent=section+(open?" ▸":" ▾");
  });
  title.setAttribute("aria-expanded","false");

  items.forEach(category=>{
   const item=document.createElement("button");
   item.type="button";
   item.className="legendItem";
   item.textContent=category;
   item.dataset.search=category.toLowerCase();

   item.addEventListener("click",()=>showLegendCategory(category));
   list.appendChild(item);
  });

  wrap.appendChild(title);
  wrap.appendChild(list);
  content.appendChild(wrap);
 });
}

document.getElementById("legendHeader").onclick=()=>{
 const body=document.getElementById("legendBody");
 const header=document.getElementById("legendHeader");
 const open=body.style.display!=="none";
 body.style.display=open?"none":"block";
 header.setAttribute("aria-expanded",String(!open));
};

document.getElementById("legendClear").onclick=()=>{
 legendLayer.clearLayers();
 document.getElementById("info").innerHTML="";
};

const legendItems = [];
document.getElementById("legendSearch").oninput=function(){
 const q=this.value.toLowerCase().trim();
 legendItems.forEach(item=>{
  item.style.display=!q || item.dataset.search.includes(q) ? "block" : "none";
 });
};

buildLegend();
legendItems.push(...document.querySelectorAll(".legendItem"));
