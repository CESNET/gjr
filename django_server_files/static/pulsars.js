// global definition of marker updater which is shared
var marker_updater;

function renderPulsar(pulsar, markerFeatureGroup) {
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
            colors: ["rgba(252, 163, 17, 0.5)", "rgba(103, 148, 54, 0.5)", "rgba(214, 40, 40, 0.5)"],
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
    if (pulsar_job_sum > 0) {
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

function playHistory_oneStep(data, keys, history_moment, history_size, range_size, markerClusterGroup) {
    if (history_moment.index >= history_size) {
        document.getElementById("history_range").value = 0;
        document.getElementById("time_label").innerHTML = `Live`;
        history_moment.index = 0;
        document.getElementById("live_button").style.display = "none";
        updateMarkersPie_realTime(markerClusterGroup)
        clearInterval(marker_updater);
        marker_updater = setInterval(() => updateMarkersPie_realTime(markerClusterGroup), 20000);
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

        // TODO: unreliable - need to make it different (dictionary does not have order you can rely on)
        const keys = Object.keys(data);

        // start rendering markers fast from moment
        marker_updater = setInterval(() => playHistory_oneStep(data, keys, history_moment, history_size, range_size, markerClusterGroup), 500);
    });
}
