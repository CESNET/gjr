// Paints legend into the map website

function  getColor(s) {
    if ( s === '0-10 jobs')
        return 'green';
    else if ( s === '10-100 jobs' )
        return 'orange';
    else
        return 'red';
}

function add_legend() {
    var legend = L.control({position: 'topright'});
    legend.onAdd = function (map) {
        var legendDiv =  L.DomUtil.create('div', 'info legend'),
            checkins = ['0-10 jobs', '10-100 jobs', '100-1000 jobs'],
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

add_legend();
