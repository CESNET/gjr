// global definition of marker updater which is shared
let marker_updater;

function renderPulsar(pulsar, markerFeatureGroup) {
    const pulsarJobTotal = pulsar.queued_jobs + pulsar.running_jobs + pulsar.failed_jobs;
    const iconSize = Math.min(200, pulsarJobTotal + 35); // Maintain max size constraint
    let minichart;
    if (pulsarJobTotal > 0) {
        minichart = L.minichart([pulsar.latitude, pulsar.longitude], {
            type: "pie",
            data: [pulsar.queued_jobs, pulsar.running_jobs, pulsar.failed_jobs],
            maxValues: "auto",
            colors: ["rgba(252, 163, 17, 0.5)", "rgba(103, 148, 54, 0.5)", "rgba(214, 40, 40, 0.5)"],
            width: iconSize,
            labels: "auto",
            transitionTime: 1
        });
    } else {
        minichart = L.marker([pulsar.latitude, pulsar.longitude], {
            icon: L.divIcon({
                className: 'runner_icon runner_icon_empty',
                html: `<b>${pulsarJobTotal}</b>`,
                iconSize: [iconSize, iconSize]
            })
        });
    }
    var longest_list = "";
    if (pulsar.longest_jobs) {
    	pulsar.longest_jobs.forEach(job => {
            longest_list += `<li>Job running tool <b>${job.tool}</b> for <b>${job.hours}</b> hours</li>`
    	});
    }
    var tools_list = "";
    if (pulsar.most_used_tools) {
    	pulsar.most_used_tools.forEach(tool => {
            tools_list += `<li><b>${tool.tool}</b> was computed by <b>${tool.job_num}</b> jobs</li>`
    	});
    }
    var users_list = "";
    if (pulsar.active_users) {
    	pulsar.active_users.forEach(user => {
            users_list += `<li>User ${user.user_id} ran ${user.job_num} jobs in last hour on this machine.</li>`
    	});
    }
    var anonym_jobs = 0;
    if (pulsar.anonymous_jobs) {
    	anonym_jobs = pulsar.anonymous_jobs;
    }
    var unique_users = 0;
    if (pulsar.unique_users) {
	unique_users = pulsar.unique_users;
    }
    const tooltipContent = `
        <h3><b>${pulsar.name}</b></h3>
        Queued jobs: <b>${pulsar.queued_jobs}</b><br>
        Running jobs: <b>${pulsar.running_jobs}</b><br>
        Failed jobs in last hour: <b>${pulsar.failed_jobs}</b><br>
        Anonymous jobs in last hour: <b>${anonym_jobs}</b><br>
        Unique users in last hour: <b>${unique_users}</b><br>
        <h5>Longest running jobs:</h5>
        ${longest_list}
        <h5>Most used tools:</h5>
        ${tools_list}
        <h5>Most active users:</h5>
        ${users_list}
    `;
    const tooltip = L.tooltip({
        content: tooltipContent,
        offset: L.point(iconSize / 2, -iconSize / 2),
        direction: 'right',
        className: 'leaflet-tooltip-own'
    });
    minichart.bindTooltip(tooltip);
    if (pulsarJobTotal > 0) {
        minichart.on('mouseover', function() {
            minichart.setOptions({
                width: iconSize * 1.2,
                colors: ["rgba(252, 163, 17, 0.8)", "rgba(103, 148, 54, 0.8)", "rgba(214, 40, 40, 0.8)"],
                pane: 'tooltipPane'
            });
        });
        minichart.on('mouseout', function() {
            minichart.setOptions({
                width: iconSize,
                colors: ["rgba(252, 163, 17, 0.5)", "rgba(103, 148, 54, 0.5)", "rgba(214, 40, 40, 0.5)"],
                pane: 'overlayPane'
            });
        });
    }
    minichart.on("click", function() {
        graph = document.getElementById("eval_graph_svg");
        if (graph) {
            graph.remove();
        }
        dividerUp();
        document.getElementById("eval-pulsar-name").innerHTML = pulsar.name;
        addEvalGraph(pulsar.name);
    });
    pulsar.chart = minichart;
    pulsar.tooltip = tooltip;
    minichart.addTo(markerFeatureGroup);
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
    markerClusterGroup.clearLayers();
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
