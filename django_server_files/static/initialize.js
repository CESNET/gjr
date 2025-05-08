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
