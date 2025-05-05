/**
 * Adds a custom legend to the specified map object. The legend includes static HTML content,
 * a dynamic pie chart visualizing job statuses, and control elements for historical data views.
 * It positions the legend at the top right of the map.
 * @param {Object} map - The Leaflet map instance to which the legend will be added.
 */
function addLegend(map) {
    var legend = L.control({ position: 'topright' });
    legend.onAdd = function () {
        var legendDiv = createLegendDiv();
        legendDiv.innerHTML = generateLegendHTML1();
        createPieChart(legendDiv);
        legendDiv.innerHTML += generateLegendHTML2();
        return legendDiv;
    };
    legend.addTo(map);
}

/**
 * Creates a div element with specific classes for styling the legend component on the map.
 * Returns a new HTML div element with the class 'info legend'.
 * @returns {HTMLElement} A div element for containing legend content.
 */
function createLegendDiv() {
    return L.DomUtil.create('div', 'info legend');
}

/**
 * Generates and returns the first portion of static HTML content for the legend.
 * This part includes the title, version information, and a description of the app's purpose.
 * @returns {string} HTML string for the first section of the legend.
 */
function generateLegendHTML1() {
    var title = '<img style="padding-left: 30px" src="static/gjr_logo.png" width="230">';
    var versionInfo = '<strong style="color: red; padding-left: 20px">ver.: 0.02 UNDER DEVELOPMENT</strong>';
    var appInfo = '<p style="padding-left: 20px">This application provides visualization of computations through European <b><a href="https://galaxyproject.org/" target="_blank" rel="noopener noreferrer">Galaxy</a></b> instance.</p>';
    return title + '<br>' + versionInfo + '<br>' + appInfo;
}

/**
 * Generates and returns the second portion of static HTML content for the legend.
 * This part includes source information, interactive controls for selecting data history windows, and playback functions.
 * @returns {string} HTML string for the second section of the legend.
 */
function generateLegendHTML2() {
    var sourceInfo = '<span style="padding-left: 20px">source: <a target="_blank" href="https://github.com/CESNET/gjr">github.com/CESNET/gjr</a></span><br>';
    var historySelection = `
        <select name="history_window" id="history_window">
            <option value="minute">last 10 minutes (average per minute)</option>
            <option value="hour">last hour (average per minute)</option>
            <option value="day">last day (average per hour)</option>
            <option value="day">last month (average per day)</option>
            <option value="day">last year (average per month)</option>
        </select>
        <button type="button" id="history_button" class="history_button" name="play_history">Play history</button>
        <input type="range" id="history_range" class="history_range" name="history_range" min="0" max="100" value="0"></input>
        <label id="time_label">Live</label>
        <button type="button" id="live_button" class="live_button" name="live_button">Return to live view</button>`;
    return sourceInfo + '<br>' + historySelection;
}

/**
 * Initializes a pie chart within the provided legend div, illustrating job queue statuses
 * such as queued, running, and failed jobs. The chart's container is styled and scaled.
 * @param {HTMLElement} legendDiv - The div element in which the pie chart will be rendered.
 */
function createPieChart(legendDiv) {
    var svgDiv = L.DomUtil.create('div', 'chart-container', legendDiv);
    svgDiv.style.width = '270px';
    svgDiv.style.height = '150px';
    svgDiv.setAttribute('id', 'chart');
    var data = [
        { label: "Queued Jobs", value: 38, color: "rgb(252, 163, 17)" },
        { label: "Running Jobs", value: 42, color: "rgb(103, 148, 54)" },
        { label: "Failed Jobs", value: 20, color: "rgb(214, 40, 40)" }
    ];
    drawPieChart(svgDiv, data);
}

/**
 * Creates and configures a pie chart using D3.js within the provided SVG div element.
 * The pie chart visually represents three categories of job statuses with color coding.
 * @param {HTMLElement} svgDiv - The SVG container div created to house the pie chart.
 * @param {Array} data - An array of objects, each representing a pie slice with its label, value, and color.
 */
function drawPieChart(svgDiv, data) {
    var width = 150, height = 150, radius = Math.min(width, height) / 2;
    var svg = d3.select(svgDiv)
        .append("svg")
        .attr("width", 300)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
    var pie = d3.pie().value(function (d) { return d.value; });
    var path = d3.arc().outerRadius(radius - 10).innerRadius(0);
    var arc = svg.selectAll(".arc")
        .data(pie(data))
        .enter().append("g")
        .attr("class", "arc");    createArcs(arc, path);
    addLabelsAndLines(svg, radius);
}

/**
 * Generates the arcs of the pie chart and associates each arc with its respective data and color.
 * Tooltips with job status labels are also added to further describe each arc.
 * @param {Object} arc - The D3.js selection containing the arc elements for pie chart data.
 * @param {Function} path - The D3.js path generator used to define the shape of the pie slices.
 */
function createArcs(arc, path) {
    arc.append("path")
        .attr("d", path)
        .style("fill", function (d) { return d.data.color; })
        .style("opacity", 0.7) // Set an initial opacity
        .on("mouseover", function (event, d) {
            d3.select(this)
              .style("opacity", 1); // Change opacity to 1 on mouseover
        })
        .on("mouseout", function (event, d) {
            d3.select(this)
              .style("opacity", 0.7); // Reset the opacity on mouseout
        });
    arc.append("title")
        .text(function (d) { return d.data.label; });
}

/**
 * Adds labeled lines to the pie chart, offering additional context by linking labels with corresponding pie slices.
 * Includes adjustments for the position of lines and text labels around the pie chart.
 * @param {Object} svg - The SVG container within which lines and labels are drawn.
 * @param {number} radius - The radius of the pie chart used for calculating label and line positions.
 */
function addLabelsAndLines(svg, radius) {
    var labels = [
        // { text: "Anonymous Jobs", color: "rgba(100, 100, 100)", offset: 0 },
        { text: "Failed Jobs", color: "rgba(255, 0, 0)", offset: Math.PI / 6 },
        { text: "Running Jobs", color: "rgba(62, 164, 16)", offset: 0 },
        { text: "Queued Jobs", color: "rgba(255, 148, 42)", offset: -1 * Math.PI / 6 }
    ];
    labels.forEach(function (label, i) {
        var x1 = choose_coordinates_for_label_x1(label.text);
        var y1 = choose_coordinates_for_label_y1(label.text);
        var xLabel = radius + 18;
        var yLabel = (i - 1.5) * 30;
        svg.append("line")
            .attr("x1", x1)
            .attr("y1", y1)
            .attr("x2", xLabel - 10)
            .attr("y2", yLabel)
            .attr("stroke", "black")
            .attr("stroke-width", 2);
        svg.append("text")
            .attr("x", xLabel - 5)
            .attr("y", yLabel + 5)
            .style("fill", label.color)
            .text(label.text)
            .style("font-size", "12px")
            .style("font-weight", "bold");
    });
    // svg.append("circle")
    //     .attr("cx", radius * Math.cos(Math.PI / 6) - 18)
    //     .attr("cy", -radius * Math.sin(Math.PI / 6) - 5)
    //     .attr("r", 20)
    //     .style("fill", "rgba(100, 100, 100)");
    // svg.append("title")
    //     .attr("id", "anonymousTooltip")
    //     .text("Anonymous Jobs");
}

/**
 * Determines and returns the x-coordinate for the initial point of labels' connecting lines to the pie chart.
 * Each label's position is calculated based on its specific category.
 * @param {string} label - The label text corresponding to a pie slice.
 * @returns {number} The x-coordinate for the start of the connecting line for the given label.
 */
function choose_coordinates_for_label_x1(label) {
    switch (label) {
        // case "Anonymous Jobs": return 45;
        case "Queued Jobs": return -20;
        case "Running Jobs": return 45;
        case "Failed Jobs": return -15;
    }
}

/**
 * Determines and returns the y-coordinate for the initial point of labels' connecting lines to the pie chart.
 * Each label's vertical placement is determined based on its category.
 * @param {string} label - The label text corresponding to a pie slice.
 * @returns {number} The y-coordinate for the start of the connecting line for the given label.
 */
function choose_coordinates_for_label_y1(label) {
    switch (label) {
        // case "Anonymous Jobs": return -45;
        case "Queued Jobs": return 20;
        case "Running Jobs": return 0;
        case "Failed Jobs": return -25;
    }
}
