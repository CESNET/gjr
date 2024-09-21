function createMap(center, zoom) {
    let map = L.map('map').setView(center, zoom);

    // L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}').addTo(map);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    // L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}').addTo(map);

    // L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);

    // L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png').addTo(map);

    // L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png').addTo(map);

    return map
}

function getMarkerColor(pulsar_job_sum) {
    if (pulsar_job_sum < 30) {
        return 'runner_icon_green';
    }
    if (pulsar_job_sum < 100) {
        return 'runner_icon_orange';
    }
    return 'runner_icon_red';
}

function updateMarkersPie(markerFeatureGroup) {
    // Send a request to the server to get the new job numbers
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        markerFeatureGroup.clearLayers();
        data.pulsars.forEach((pulsar, idx) => {
            var pulsar_job_sum = pulsar.queued_jobs + pulsar.running_jobs + pulsar.failed_jobs
            var maximal_icon_size = 200;
            var minimal_icon_size = 35;
            var icon_size = pulsar_job_sum + minimal_icon_size > maximal_icon_size ? maximal_icon_size : pulsar_job_sum + minimal_icon_size;
            var minichart;

            if (pulsar_job_sum > 0) {
                minichart = L.minichart([pulsar.latitude, pulsar.longitude], {
                    type: "pie",
                    data: [pulsar.queued_jobs, pulsar.running_jobs, pulsar.failed_jobs],
                    maxValues: "auto",
                    colors: ["rgba(255, 148, 42, 0.5)", "rgba(62, 164, 16, 0.5)", "rgba(255, 0, 0, 0.5)"],
                    width: icon_size,
                    labels: "auto",
                    transitionTime: 0
                });
            } else {
                minichart = L.marker([pulsar.latitude, pulsar.longitude], {
                    icon: L.divIcon({
                        className: 'runner_icon runner_icon_empty',
                        html: '<b>' + pulsar_job_sum + '</b>',
                        iconSize: [icon_size, icon_size]
                    })
                });
            }

            minichart.addTo(markerFeatureGroup);
            minichart.bindTooltip(L.tooltip([pulsar.latitude, pulsar.longitude], {
                content: `runner name: <b>${pulsar.name}</b><br>queued jobs: <b>${pulsar.queued_jobs}</b><br>running jobs: <b>${pulsar.running_jobs}</b><br>failed jobs: <b>${pulsar.failed_jobs}</b>`,
                offset: L.point((icon_size / 2), -(icon_size / 2)),
                direction: 'right'
            }));
            // event listeners
            minichart.on('mouseover', function () {
                minichart.setOptions({
                    width: icon_size * 1.2,
                    colors: ["rgba(255, 148, 42, 0.8)", "rgba(62, 164, 16, 0.8)", "rgba(255, 0, 0, 0.8)"],
                    pane: 'tooltipPane'

                });
            });
            minichart.on('mouseout', function () {
                minichart.setOptions({
                    width: icon_size,
                    colors: ["rgba(255, 148, 42, 0.5)", "rgba(62, 164, 16, 0.5)", "rgba(255, 0, 0, 0.5)"],
                    pane: 'overlayPane'
                });
            });
        })
    })
}

function updateMarkersCircles(markerFeatureGroup) {
    // Send a request to the server to get the new job numbers
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        markerFeatureGroup.clearLayers();
        data.pulsars.forEach((pulsar, idx) => {
            var pulsar_job_sum = pulsar.queued_jobs + pulsar.running_jobs + pulsar.failed_jobs
            var icon = getMarkerColor(pulsar_job_sum);
            var maximal_icon_size = 150;
            var icon_size = pulsar_job_sum / 2 + 20 > maximal_icon_size ? maximal_icon_size : pulsar_job_sum / 2 + 20;

            L.marker([pulsar.latitude, pulsar.longitude], {
                icon: L.divIcon({
                    className: 'runner_icon ' + icon,
                    html: '<b>' + pulsar_job_sum + '</b>',
                    iconSize: [icon_size, icon_size]
                })
            }).addTo(markerFeatureGroup)
              .bindTooltip(`runner name: <b>${pulsar.name}</b><br>queued jobs: <b>${pulsar.queued_jobs}</b><br>running jobs: <b>${pulsar.running_jobs}</b><br>failed jobs: <b>${pulsar.failed_jobs}</b>`);
        })
    })
}

function  getColor(s) {
    if ( s === '0-30 jobs' || s === 'running jobs')
        return 'green';
    else if ( s === '30-100 jobs' || s === 'queued jobs')
        return 'orange';
    else
        return 'red';
}

function addLegendCircle(map) {
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

function addLegendPie(map) {
    var legend = L.control({position: 'topright'});
    legend.onAdd = function (map) {
        var legendDiv =  L.DomUtil.create('div', 'info legend'),
            checkins = ['running jobs', 'queued jobs', 'failed jobs'],
            title = '<strong>Galaxy Visualization</strong>',
            labels = ['<p>Hello to our galaxy visualization tool from CESNET!</p>'];
        for (var i=0; i < checkins.length; i++) {
            labels.push(
                '<i class="square" style="background:' + getColor(checkins[i]) + '"></i><p>' + checkins[i] + '</p>')
        }
        labels.push(`<form action="/play-history/" method="post">
                        {% csrf_token %}
                        {{ PlayHistory }}
                        <button class="history_button" type="submit" name="play_history">Play history</button>
                        <input class="history_range" type="range" min="0" max="100" value="100"></input>
                     </form>`);
        legendDiv.innerHTML = title + '<br>' + labels.join('<br>');
        return legendDiv;
    }
    legend.addTo(map);
}

function get_rand_color() {
    return "#"+(((1+Math.random())*(1<<24)|0).toString(16)).substr(-6);
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
        { name: 'usegalaxy.eu', coordinates: [48.9731131, 9.3016003], color: get_rand_color() },
        // { name: 'usegalaxy.org', coordinates: [43.000000, -75.000000], color: get_rand_color() },
        // { name: 'usegalaxy.au', coordinates: [-33.865143, 151.209900], color: get_rand_color() },
        { name: 'usegalaxy.cz', coordinates: [50.2117769, 15.3615611], color: get_rand_color() },
        { name: 'usegalaxy.uk', coordinates: [51.5188083, 0.1403647], color: get_rand_color() },
        { name: 'usegalaxy.se', coordinates: [59.8583539, 17.6291306], color: get_rand_color() },
        { name: 'usegalaxy.sp', coordinates: [40.616775, -3.703790], color: get_rand_color() },
        { name: 'usegalaxy.fr', coordinates: [48.6107856, 1.6836897], color: get_rand_color() },
        { name: 'usegalaxy.lv', coordinates: [56.9479739, 24.0932114], color: get_rand_color() }
    ];

    galaxies.forEach(galaxy => {
        L.marker(galaxy.coordinates, {icon: galaxy_icon}).addTo(map).bindPopup(`<a href="https://${galaxy.name}"><b>${galaxy.name}</b></a>`);
    });

    // lines from galaxy to pulsars
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        data.pulsars.forEach((pulsar, idx) => {
            L.polyline([
                galaxies.find(p => p.name == pulsar.galaxy).coordinates,
                [pulsar.latitude, pulsar.longitude]],
                { color: galaxies.find(p => p.name == pulsar.galaxy).color }
            ).addTo(map)
        })
    })
}
