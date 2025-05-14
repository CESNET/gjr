/**
 * Initializes the SVG element and defines the margin and dimensions.
 * @returns {Object} Contains the SVG element and its dimensions.
 */
function initializeSVG() {
    const container = document.getElementById("eval-graph");
    const margin = { top: 5, right: 10, bottom: 45, left: 40 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom;
    const svg = d3.select("#eval-graph")
        .append("svg")
            .attr("width", container.clientWidth)
            .attr("height", container.clientHeight)
            .attr("id", "eval_graph_svg")
        .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`)
            .attr("id", "eval_graph_svg");
    return { svg, width, height, margin };
}

/**
 * Creates and defines the x and y scales.
 * @param {Array} data - Array of data sets.
 * @param {number} width - Width of the SVG element.
 * @param {number} height - Height of the SVG element.
 * @returns {Object} Contains the x and y scales.
 */
function createScales(data, width, height) {
    const x = d3.scaleTime()
        .domain(d3.extent(data[0], d => d.date))
        .range([0, width]);
    // Use d3.scaleLog to create a logarithmic scale for the y-axis
    const y = d3.scaleLog()
        .domain([
            0.1, // Ensure the minimum is greater than zero for log scale
            d3.max(data.flat(), d => d.value) || 1 // Avoid log(0) and handle empty data gracefully
        ])
        .range([height, 0])
        .clamp(true); // Optionally, clamp to avoid negative values that are outside of the domain

    return { x, y };
}

/**
 * Appends the X and Y axes to the SVG element.
 * @param {Object} svg - The SVG element.
 * @param {Object} x - The x scale.
 * @param {Object} y - The y scale.
 * @param {number} height - Height of the SVG element.
 */
function appendAxes(svg, x, y, height) {
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5));
    svg.append("g")
        .call(d3.axisLeft(y)
            .ticks(5, "~s") // Use a format suitable for log scales
        );
}

/**
 * Adds grid lines to the chart.
 * @param {Object} svg - The SVG element.
 * @param {Object} x - The x scale.
 * @param {Object} y - The y scale.
 * @param {number} width - Width of the SVG element.
 * @param {number} height - Height of the SVG element.
 */
function addGridLines(svg, x, y, width, height) {
    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .ticks(5)
            .tickSize(-height)
            .tickFormat(""));
    svg.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y)
            .ticks(5)
            .tickSize(-width)
            .tickFormat(""));
}

/**
 * Draws the lines on the chart for each dataset.
 * @param {Object} svg - The SVG element.
 * @param {Array} dataSets - Array of datasets.
 * @param {Object} x - The x scale.
 * @param {Object} y - The y scale.
 * @param {Array} colors - Array of colors for each dataset.
 */
function drawLines(svg, dataSets, x, y, colors) {
    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.value));
    dataSets.forEach((dataSet, index) => {
        svg.append("path")
            .datum(dataSet)
            .attr("fill", "none")
            .attr("stroke", colors[index])
            .attr("stroke-width", 3)
            .attr("d", line)
            .attr("id", "graphline");
    });
}

/**
 * Adds interactivity to lines with a tooltip.
 * @param {Object} svg - The SVG element.
 * @param {Object} x - The x scale.
 * @param {Object} y - The y scale.
 */
function addInteractivity(svg, x, y) {
    const tooltip = d3.select("#eval-graph")
        .append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    svg.selectAll("#graphline")
        .on("mouseover", function(event) {
            d3.select(this).attr("stroke-width", 6);
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
        })
        .on("mousemove", function(event) {
            const [mouseX, mouseY] = d3.pointer(event);
            const xm = x.invert(mouseX);
    const ym = y.invert(mouseY);
            tooltip.html(`Date:<br><b>${d3.timeFormat("%B %d, %Y")(xm)}</b><br>Value:<br><b>${ym.toFixed(2)}</b>`)
                .style("left", `${event.pageX}px`)
                .style("top", `${event.pageY - 28}px`);
        })
        .on("mouseout", function() {
            d3.select(this).attr("stroke-width", 3);
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
}

/**
 * Adds a chart legend to distinguish different datasets.
 * @param {Object} svg - The SVG element.
 * @param {number} width - Width of the SVG element.
 * @param {Array} labels - Array of labels for the legend.
 * @param {Array} colors - Array of colors representing each dataset.
 */
function drawLegend(svg, width, labels, colors) {
    // Create a tooltip div container
    const tooltip = d3.select("#eval-graph")
        .append("div")
        .attr("class", "tooltiplegend")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("pointer-events", "none")
        .style("background-color", "white")
        .style("border", "1px solid #ccc")
        .style("padding", "5px")
        .style("border-radius", "5px");

    const legend = svg.append("g")
        .attr("font-family", "sans-serif")
        .attr("font-size", 11)
        .attr("font-weight", "bold")
        .attr("text-anchor", "end")
        .selectAll("g")
        .data(labels)
        .enter().append("g")
        .attr("transform", (d, i) => `translate(0, ${i * 20})`);

    legend.append("rect")
        .attr("x", width - 19)
        .attr("width", 19)
        .attr("height", 19)
        .style("cursor", "pointer")
        .attr("fill", (d, i) => colors[i])
        .on("mouseover", (event, d) => {
            drawTooltipLegend(tooltip, d)
        })
        .on("click", (event, d) => {
            window.open("https://jsspp.org/papers23/Boezennec.pdf#page=3", '_blank').focus();
        });

    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9.5)
        .attr("dy", "0.32em")
        .style("cursor", "pointer")
        .attr("fill", "white")
        .text(d => d)
        .on("mouseover", (event, d) => {
           drawTooltipLegend(tooltip, d);
        })
        .on("mousemove", (event) => {
            tooltip.style("left", `${event.pageX - tooltip.node().offsetWidth - 40}px`)
                .style("top", `${event.pageY - 80}px`);
        })
        .on("mouseout", () => {
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        })
        .on("click", (event, d) => {
            window.open("https://jsspp.org/papers23/Boezennec.pdf#page=3", '_blank').focus();
        });
}

/**
 * Adds a tooltip to legend to describe different metrics.
 * @param {Object} tooltip - html tooltip object.
 * @param {String} metric - String representing metric.
 */
function drawTooltipLegend(tooltip, metric) {
     tooltip.transition()
        .duration(200)
        .style("opacity", 0.9)
    if (metric == "Mean Slowdown") {
        tooltip.html(`<b>${metric}</b>
                <br>We take all jobs for each four hours (starts in this window and ends in this window) and for every job J we calculate slowdown S which is ratio of the time it spent in the system over its real execution time. Ten we will make average for all these slowdowns in the time window.
                <br>For more info click on the legend.`
            ).style("left", `${event.pageX - tooltip.node().offsetWidth - 40}px`)
            .style("top", `${event.pageY - 80}px`);
        }
    if (metric == "Bounded Slowdown") {
        tooltip.html(`<b>${metric}</b>
                <br>Similar to mean slowdown but surges extreme cases.
                <br>For more info click on the legend.`
            ).style("left", `${event.pageX - tooltip.node().offsetWidth - 40}px`)
            .style("top", `${event.pageY - 80}px`);
    }
    if (metric == "Response Time") {
        tooltip.html(`<b>${metric}</b>
                <br>Response time of a job J is the duration between the submission of the job and its completition. Same as for bounded and mean slowdown are are doing average for each for hours.
                <br>For more info click on the legend.`
            ).style("left", `${event.pageX - tooltip.node().offsetWidth - 40}px`)
            .style("top", `${event.pageY - 80}px`);
    }
}

/**
 * Main function to add the evaluation graph to the page.
 * @param {Array} dataSets - Array of data sets to be plotted.
 */
function addEvalGraph(pulsar_name) {
    var url = `/scheduling-analysis/${pulsar_name}/`;
    var dataSets = []
    fetch(url, { method: "GET" }).then(response => response.json()).then(data => {
        const convertDatesInDataset = dataset => {
            if (dataset) {
                dataset.forEach(entry => {
                    entry.date = new Date(entry.date);
                });
            }
        };
        convertDatesInDataset(data['mean_slowdown']);
        convertDatesInDataset(data['bounded_slowdown']);
        convertDatesInDataset(data['response_time']);
        dataSets = [data['mean_slowdown'], data['bounded_slowdown'], data['response_time']];
        const isDataEmpty = dataSets.every(dataSet => !dataSet || dataSet.length === 0);
        const { svg, width, height } = initializeSVG();
        if (isDataEmpty) {
            svg.append("text")
                .attr("x", width / 2)
                .attr("y", height / 2)
                .attr("font-family", "sans-serif")
                .attr("text-anchor", "middle")
                .attr("dominant-baseline", "central")
                .style("font-size", "40px")
                .style("fill", "darkgray")
                .text("No Data");
        } else {
            const labels = ["Mean Slowdown", "Bounded Slowdown", "Response Time"];
            const colors = ["rgb(42, 157, 143)", "rgb(165, 56, 96)", "rgb(114, 9, 183)"];
            const { x, y } = createScales(dataSets, width, height);
            appendAxes(svg, x, y, height);
            addGridLines(svg, x, y, width, height);
            drawLines(svg, dataSets, x, y, colors);
            addInteractivity(svg, x, y);
            drawLegend(svg, width, labels, colors);
        }
    });
}
