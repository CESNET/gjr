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
    // Send a request to the server to get the new latitude and longitude data
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        let prevLatLons = []
        markerFeatureGroup.eachLayer(layer => layer.hasOwnProperty('_latlng') && prevLatLons.push(layer._latlng))
        markerFeatureGroup.clearLayers();
        data.pulsars.forEach((pulsar, idx) => {
            let prevLatLon = [prevLatLons[idx].lat, prevLatLons[idx].lng]
            let newLatLon = [pulsar.latitude, pulsar.longitude];
            var icon = getMarkerColor(pulsar);
            var maximal_icon_size = 150;
            var icon_size = pulsar.job_num / 2 + 20 > maximal_icon_size ? maximal_icon_size : pulsar.job_num / 2 + 20;
            L.marker(newLatLon, {
                icon: L.divIcon({
                    className: 'runner_icon ' + icon,
                    html: '<b>' + pulsar.job_num + '</b>',
                    iconSize: [icon_size, icon_size]
                })
            }).addTo(markerFeatureGroup)
              .bindPopup(`<b>Runner name: ${pulsar.name}<br>Job number: ${pulsar.job_num}</b>`)
              .bindTooltip(`<b>${pulsar.name}</b>`);
            // L.polyline([prevLatLon, newLatLon]).addTo(markerFeatureGroup)
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
        { name: 'Europe - galaxy.eu', coordinates: [56.7584994, 0.7277719] },
        { name: 'USA - galaxy.org', coordinates: [43.000000, -75.000000] },
        { name: 'Australia - galaxy.au', coordinates: [-33.865143, 151.209900] },
        { name: 'Czechia - galaxy.cz', coordinates: [50.2117769, 15.3615611] }
    ];
    // Pulsar servers points
    const eu_pulsars = [
        { name: 'Freiburg - Miras pulsar', coordinates: [48.1731131, 8.9016003] },
        { name: 'Freiburg - Snajays pulsar', coordinates: [48.1731131, 9] },
        { name: 'Rennes - GenOuest bioinformatics', coordinates: [48.1107856, 1.6836897] },
        { name: 'Bari - RECAS', coordinates: [41.9028, 12.4964] },
        { name: 'Bari - RECAS 2', coordinates: [42, 12.4964] },
        { name: 'Bari - INFN', coordinates: [41.9028, 12.6] },
        { name: 'Brussel - VIB', coordinates: [50.8476, 4.3572] },
        { name: 'Prague - MetaCentrum', coordinates: [50.0755, 14.4378] },
        { name: 'Bratislava - IISAS', coordinates: [48.148598, 17.107748] },
        { name: 'Barcelona - BSC-CNS', coordinates: [40.416775, -3.703790] },
        { name: 'Ankara - TUBITAK ULAKBIM', coordinates: [39.2233947, 28.7209361] },
        { name: 'Krakow - Cyfronet', coordinates: [52.237049, 21.017532] },
        { name: 'Herakilon-Crete - HCMR', coordinates: [35.3369294, 25.1281525] }
    ];
    galaxies.forEach(galaxy => {
        L.marker(galaxy.coordinates, {icon: galaxy_icon}).addTo(map).bindPopup(`<b>${galaxy.name}</b>`).bindTooltip(`<b>${galaxy.name}</b>`);
    });
    // eu lines
    eu_pulsars.forEach(pulsar => {
        L.polyline([galaxies.find(p => p.name == "Europe - galaxy.eu").coordinates, pulsar.coordinates], { color: 'black' })
        .addTo(map)
    });
}
