// js leaflet map programming

var map = L.map("map").setView([50, 8], 5);

// map background
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
}).addTo(map);

// graphics

// custom markers

var galaxy_icon = L.icon({
    iconUrl: 'graphics/galaxy_logo.png',
    iconSize:     [50, 50], // size of the icon
    iconAnchor:   [22, 55], // point of the icon which will correspond to marker's location
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

var pulsar_icon = L.icon({
    iconUrl: 'graphics/pulsar_logo.png',
    iconSize:     [30, 30],
    iconAnchor:   [15, 15],
    popupAnchor:  [15, 15]
});

const runner_icon = L.Icon.extend({
    options: {
        iconSize:     [20, 20],
        iconAnchor:   [10, 10],
        popupAnchor:  [10, 10]
    }
});

var runner_icon_green = new runner_icon({iconUrl: 'graphics/runner_logo_green.png'}),
    runner_icon_orange = new runner_icon({iconUrl: 'graphics/runner_logo_orange.png'}),
    runner_icon_red = new runner_icon({iconUrl: 'graphics/runner_logo_red.png'});

// add points

galaxies.forEach(galaxy => {
    L.marker(galaxy.coordinates, {icon: galaxy_icon}).addTo(map).bindPopup(`<b>${galaxy.name}</b>`).bindTooltip(`<b>${galaxy.name}</b>`);
});


eu_pulsars.forEach(pulsar => {
    L.marker(pulsar.coordinates, {icon: pulsar_icon}).addTo(map).bindPopup(`<b>${pulsar.name}</b>`).bindTooltip(`<b>${pulsar.name}</b>`);
});


czech_runners.forEach(runner => {
    var icon = runner_icon_red;
    if (runner.job_num < 100) {
        icon = runner_icon_orange;
    }
    if (runner.job_num < 10) {
        icon = runner_icon_green;
    }
    L.marker(runner.coordinates, {icon: icon}).addTo(map).bindPopup(`<b>Runner name: ${runner.name}<br>Job number: ${runner.job_num}</b>`).bindTooltip(`<b>${runner.name}</b>`);
});

// tree lines between points

// eu lines
eu_pulsars.forEach(pulsar => {
    L.polyline([galaxies.find(p => p.name == "Europe - galaxy.eu").coordinates, pulsar.coordinates], { color: 'black' })
        .addTo(map)
});

// czech lines
czech_runners.forEach(runner => {
    L.polyline([eu_pulsars.find(p => p.name == "CESNET - Czech Pulsar").coordinates, runner.coordinates], { color: 'blue' })
        .addTo(map)
});

// Animation

var planeRoute1 = JSON.parse('[{"lat":56.7584994,"lng":0.7277719},{"lat":43.000000,"lng":-75.000000}]');

var seqGroup = L.motion.seq([
    L.motion.seq([
        L.motion.polyline(planeRoute1, {
            color:"indigo"
        }, null, {
            removeOnEnd: false,
            icon: L.divIcon({html: "<i class='fa fa-plane fa-2x' aria-hidden='true' motion-base='-43'></i>", iconSize: L.point(19, 24)})
        }).motionDuration(5000),
    ])
]).addTo(map);

setTimeout(function () {
    seqGroup.motionStart();
}, 1000);

// legend

function  getColor(s) {
    if ( s === '0-10 jobs')
        return 'green';
    else if ( s === '10-100 jobs' )
        return 'orange';
    else
        return 'red';
}

var legend = L.control({position: 'topright'});


legend.onAdd = function (map) {
    var legendDiv =  L.DomUtil.create('div', 'info legend'),
        checkins = ['0-10 jobs', '10-100 jobs', '100-1000 jobs'],
        title = '<strong>Galaxy Visualization</strong>',
        labels = ['<p>Hello to our galaxy visualization tool from CESNET!</p>'];

    for ( var i=0; i < checkins.length; i++) {
        labels.push(
            '<i class="square" style="background:' + getColor(checkins[i]) + '"></i><p>' + checkins[i] + '</p>')
    }

    legendDiv.innerHTML = title + '<br>' + labels.join('<br>');

    return legendDiv;
}

legend.addTo(map);
