// global definition of marker updater which is shared
var marker_updater;

function createMap(center, zoom) {
    let map = L.map('map').setView(center, zoom);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
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

function renderPulsar(pulsar, markerFeatureGroup) {

    // TODO remove later
    // if (pulsar.galaxy != "usegalaxy.eu") {
    //     return;
    // }

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
}

function updateMarkersPie_realTime(markerFeatureGroup) {
    // Send a request to the server to get the new job numbers
    fetch('/pulsar-positions/').then(response => response.json()).then(data => {
        markerFeatureGroup.clearLayers();
        data.pulsars.forEach(pulsar => {
            renderPulsar(pulsar, markerFeatureGroup);
        });
    });
}

// TODO !!!!!!!!!! SOME PROBLEM WITH marker updater - when is Play history runned second time, marker updater is not cleared and there run two instances -> maybe make object in index script with marker updater as a attribute and then change it serially
// TODO move this right into python views so I do not need to get whole history, just what I need right in SQL (get just history I need from history moment)
function playHistory_oneStep(data, keys, history_moment, history_size, range_size, markerClusterGroup) {
    if (history_moment.index >= history_size) {
        document.getElementById("history_range").value = 0;
        document.getElementById("time_label").innerHTML = `Live`;
        history_moment.index = 0;
        document.getElementById("live_button").style.display = "none";
        clearInterval(marker_updater);
        marker_updater = setInterval(() => updateMarkersPie_realTime(markerClusterGroup), 3500);
        return;
    }
    var timestamp = keys[history_moment.index];
    var arrayOfPulsars = data[timestamp];
    // change range history and label due to rendered data entries
    document.getElementById("time_label").innerHTML = `${timestamp}`;
    document.getElementById("history_range").value = Math.round(history_moment.index / (history_size / range_size));
    markerClusterGroup.clearLayers(); // TODO: CLEAR LAYERS WITHOUT ZEROES
    arrayOfPulsars.forEach(pulsar => {
        renderPulsar(pulsar, markerClusterGroup);
    });
    history_moment.index++;
}

function updateMarkersPie_playHistory(markerClusterGroup) {
    // stop real time view
    clearInterval(marker_updater);
    document.getElementById("live_button").style.display = "inline-block";
    var moment = document.getElementById("history_range").value;
    var history_window = document.getElementById("history_window").value;
    var url = `/play-history/${moment}/${history_window}/`;
    fetch(url, { method: "GET" }).then(response => response.json()).then(data => {
        // calculate moment to data entries
        var history_size = Object.keys(data).length;
        var range_size = document.getElementById("history_range").getAttribute("max");
        var history_moment_index = Math.round((history_size / range_size) * moment);
        var history_moment = { index: history_moment_index };

        // TODO also print current timestamp to the left upper corner -> I need to put there, style it in css, and position it inc css in base.html some text window and change it every time it changes, but I do not want to have there timestamp in live view -> in live view tere will be just LIVE, or something like that in TV news

        // TODO: unreliable - need to make it different (dictionary does not have order you can rely on)
        const keys = Object.keys(data);

        // start rendering markers fast from moment
        marker_updater = setInterval(() => playHistory_oneStep(data, keys, history_moment, history_size, range_size, markerClusterGroup), 500);
    });
}

function showHistoryMoment(markerClusterGroup) {
    // stop real time view
    clearInterval(marker_updater);
    var moment = document.getElementById("history_range").value;
    // calculate moment to data entries
    var history_size = Object.keys(data).length;
    var range_size = document.getElementById("history_range").getAttribute("max");
    var history_moment_index = Math.round((history_size / range_size) * moment);
    var history_moment = { index: history_moment_index };
    var url = `/show-history-moment/${moment}/`
    fetch(url, { method: "GET" }).then(response => response.json()).then(data => {
        var timestamp = keys[0];
        var pulsar = data[timestamp];
        // change range history and label due to rendered data entries
        document.getElementById("time_label").innerHTML = `${timestamp}`;
        document.getElementById("history_range").value = Math.round(history_moment.index / (history_size / range_size));
        markerClusterGroup.clearLayers();
        renderPulsar(pulsar, markerClusterGroup);
    });
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
        labels.push(
            `<select name="history_window" id="history_window">
                <option value="hour">last hour</option>
                <option value="day">last day</option>
                <option value="month">last month</option>
                <option value="year">last year</option>
            </select>
            <button type="button" id="history_button" class="history_button" name="play_history">Play history</button>
            <input type="range" id="history_range" class="history_range" name="history_range" min="0" max="100" value="0"></input>
            <label id="time_label">Live</label>
            <button type="button" id="live_button" class="live_button" name="live_button">Return to live veiw</button>`
        );
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
        // { name: 'usegalaxy.cz', coordinates: [50.2117769, 15.3615611], color: get_rand_color() },
        // { name: 'usegalaxy.uk', coordinates: [51.5188083, 0.1403647], color: get_rand_color() },
        // { name: 'usegalaxy.se', coordinates: [59.8583539, 17.6291306], color: get_rand_color() },
        // { name: 'usegalaxy.sp', coordinates: [40.616775, -3.703790], color: get_rand_color() },
        // { name: 'usegalaxy.fr', coordinates: [48.6107856, 1.6836897], color: get_rand_color() },
        // { name: 'usegalaxy.lv', coordinates: [56.9479739, 24.0932114], color: get_rand_color() }
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
