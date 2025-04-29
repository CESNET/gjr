function add_galaxy_nodes(map, galaxy_icon_path, galaxies) {
    var galaxy_icon = L.icon({
        iconUrl: galaxy_icon_path,
        iconSize:     [50, 50],
        iconAnchor:   [22, 55],
        popupAnchor:  [-3, -76]
    });

    galaxies.forEach((galaxy, idx) => {
        L.marker([galaxy.latitude, galaxy.longitude], {icon: galaxy_icon}).addTo(map).bindPopup(`<a href="https://${galaxy.name}"><b>${galaxy.name}</b></a>`);
        galaxy.linecolor = "#80aaff";
    })
}

function add_galaxy_to_pulsars_polylines(map, galaxies, pulsars) {
    // lines from galaxy to pulsars
    pulsars.forEach((pulsar, idx) => {
        var galaxy = galaxies.find(p => p.name == pulsar.galaxy)
        var polyline = L.polyline([
            [galaxy.latitude, galaxy.longitude],
            [pulsar.latitude, pulsar.longitude]],
            { color: galaxy.linecolor }
        );
        polyline.addTo(map);
    })
}

function renderPulsars(pulsars, markerFeatureGroup, map) {
    markerFeatureGroup.clearLayers();
    pulsars.forEach(pulsar => {
        // renderPulsar(pulsar).addTo(markerFeatureGroup);
        markerFeatureGroup.addLayer(renderPulsar(pulsar));
    });
}
/*
function renderPulsar(pulsar) {
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
            transitionTime: 2
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
    pulsar.tooltip = L.tooltip([pulsar.latitude, pulsar.longitude], {
        content: `<h3><b>${pulsar.name}</b></h3>
                  Queued jobs: <b>${pulsar.queued_jobs}</b><br>
                  Running jobs: <b>${pulsar.running_jobs}</b><br>
                  Failed jobs in last hour: <b>${pulsar.failed_jobs}</b><br>
                  Anonymous jobs: <b${pulsar.anonymous_jobs}</b><br>
                  Unique users: <b${pulsar.unique_users}</b><br>`,
        offset: L.point((icon_size / 2), -(icon_size / 2)),
        direction: 'right'
    })
    minichart.bindTooltip(pulsar.tooltip);
    // event listeners
    if (pulsar_job_sum > 0) {
        minichart.on('mouseover', function () {
            minichart.setOptions({
                width: icon_size * 1.2,
                colors: ["rgba(252, 163, 17, 0.8)", "rgba(103, 148, 54, 0.8)", "rgba(214, 40, 40, 0.8)"],
                pane: 'tooltipPane'
            });
        });
        minichart.on('mouseout', function () {
            minichart.setOptions({
                width: icon_size,
                colors: ["rgba(252, 163, 17, 0.5)", "rgba(103, 148, 54, 0.5)", "rgba(214, 40, 40, 0.5)"],
                pane: 'overlayPane'
            });
        });
    }
    return minichart;
}*/

function renderPulsar(pulsar) {
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

    const tooltipContent = `
        <h3><b>${pulsar.name}</b></h3>
        Queued jobs: <b>${pulsar.queued_jobs}</b><br>
        Running jobs: <b>${pulsar.running_jobs}</b><br>
        Failed jobs in last hour: <b>${pulsar.failed_jobs}</b><br>
        Anonymous jobs: <b>${pulsar.anonymous_jobs}</b><br>
        Unique users: <b>${pulsar.unique_users}</b><br>
    `;

    const tooltip = L.tooltip({
        content: tooltipContent,
        offset: L.point(iconSize / 2, -iconSize / 2),
        direction: 'right'
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

    pulsar.chart = minichart;
    pulsar.tooltip = tooltip;

    return minichart;
}
