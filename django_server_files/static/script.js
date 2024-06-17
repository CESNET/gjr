function createMap(center, zoom) {
    let map = L.map('map').setView(center, zoom);
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}').addTo(map);
    return map
}

function getMarkerColor(runner) {
    if (runner.job_num < 30) {
        return 'runner_icon_green';
    }
    if (runner.job_num < 100) {
        return 'runner_icon_orange';
    }
    return 'runner_icon_red';
}

function updateMarkers(markerFeatureGroup) {
    // Send a request to the server to get the new job numbers
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        markerFeatureGroup.clearLayers();
        data.pulsars.forEach((pulsar, idx) => {
            var icon = getMarkerColor(pulsar);
            var maximal_icon_size = 150;
            var icon_size = pulsar.job_num / 2 + 20 > maximal_icon_size ? maximal_icon_size : pulsar.job_num / 2 + 20;
            L.marker([pulsar.latitude, pulsar.longitude], {
                icon: L.divIcon({
                    className: 'runner_icon ' + icon,
                    html: '<b>' + pulsar.job_num + '</b>',
                    iconSize: [icon_size, icon_size]
                })
            }).addTo(markerFeatureGroup)
              .bindTooltip(`<b>Runner name: ${pulsar.name}<br>Job number: ${pulsar.job_num}</b>`);
        })
    })
}

function  getColor(s) {
    if ( s === '0-30 jobs')
        return 'green';
    else if ( s === '30-100 jobs' )
        return 'orange';
    else
        return 'red';
}

function addLegend(map) {
    var legend = L.control({position: 'topright'});
    legend.onAdd = function (map) {
        var legendDiv =  L.DomUtil.create('div', 'info legend'),
            checkins = ['0-30 jobs', '30-100 jobs', '100-1000 jobs'],
            title = '<strong>Galaxy Visualization</strong>',
            labels = ['<p>Hello to our galaxy visualization tool from CESNET!</p>'];
        for (var i=0; i < checkins.length; i++) {
            labels.push(
                '<i class="square" style="background:' + getColor(checkins[i]) + '"></i><p>' + checkins[i] + '</p>')
        }
        legendDiv.innerHTML = title + '<br>' + labels.join('<br>');
        return legendDiv;
    }
    legend.addTo(map);
}

function add_galaxy_eu_node_and_its_polylines(map, galaxy_icon_path) {
    var galaxy_icon = L.icon({
        iconUrl: galaxy_icon_path,
        iconSize:     [50, 50],
        iconAnchor:   [22, 55],
        popupAnchor:  [-3, -76]
    });
    // Galaxy servers points
    const galaxies = [
        { name: 'usegalaxy.eu', coordinates: [51.8897767, 10.4616589] }/*,
        { name: 'USA - galaxy.org', coordinates: [43.000000, -75.000000] },
        { name: 'Australia - galaxy.au', coordinates: [-33.865143, 151.209900] },
        { name: 'Czechia - galaxy.cz', coordinates: [50.2117769, 15.3615611] }*/
    ];

    galaxies.forEach(galaxy => {
        L.marker(galaxy.coordinates, {icon: galaxy_icon}).addTo(map).bindPopup(`<a href="https://${galaxy.name}"><b>${galaxy.name}</b></a>`);
    });

    // lines from galaxy to pulsars
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        data.pulsars.forEach((pulsar, idx) => {
            L.polyline([galaxies.find(p => p.name == "usegalaxy.eu").coordinates, [pulsar.latitude, pulsar.longitude]], { color: 'black' })
                .addTo(map)
        })
    })
}
