// js leaflet map programming

var map = L.map("map").setView([50, 8], 5);

// map background
L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}').addTo(map);

// graphics

// custom markers

var galaxy_icon = L.icon({
    iconUrl: 'graphics/galaxy_logo.png',
    iconSize:     [50, 50],
    iconAnchor:   [22, 55],
    popupAnchor:  [-3, -76]
});

var pulsar_icon = L.icon({
    iconUrl: 'graphics/pulsar_logo.png',
    iconSize:     [30, 30],
    iconAnchor:   [15, 15],
    popupAnchor:  [15, 15]
});

// add points

galaxies.forEach(galaxy => {
    L.marker(galaxy.coordinates, {icon: galaxy_icon}).addTo(map).bindPopup(`<b>${galaxy.name}</b>`).bindTooltip(`<b>${galaxy.name}</b>`);
});


eu_pulsars.forEach(pulsar => {
    L.marker(pulsar.coordinates, {icon: pulsar_icon}).addTo(map).bindPopup(`<b>${pulsar.name}</b>`).bindTooltip(`<b>${pulsar.name}</b>`);
});


function add_runners(runners) {
    runners.forEach(runner => {
        var icon = 'runner_icon_red';
        if (runner.job_num < 100) {
            icon = 'runner_icon_orange';
        }
        if (runner.job_num < 10) {
            icon = 'runner_icon_green';
        }

        L.marker(runner.coordinates, {
            icon: L.divIcon({
                className: 'runner_icon ' + icon,
                html: '<b>' + runner.job_num + '</b>',
                iconSize: [runner.job_num / 2, runner.job_num / 2]
            })
        }).addTo(map)
        .bindPopup(`<b>Runner name: ${runner.name}<br>Job number: ${runner.job_num}</b>`)
        .bindTooltip(`<b>${runner.name}</b>`);
    });
}

add_runners(czech_runners);

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
