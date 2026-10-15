// Esri Dark Gray Canvas
var dark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
});

// Esri Light Gray Canvas
var light = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 16,
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ'
});

var baseMaps = {
    "Dark theme": dark,
    "Light theme": light
};

function createMap(center, zoom) {
    let map = L.map('map', { layers: [light] }).setView(center, zoom);
    L.control.layers(baseMaps, null, { position: 'topleft' }).addTo(map);
    return map;
}