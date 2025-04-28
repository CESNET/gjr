// Sample data
const data1 = [
    { date: new Date(2023, 0, 1), value: 30 },
    { date: new Date(2023, 1, 1), value: 50 },
    { date: new Date(2023, 2, 1), value: 80 }
];    const data2 = [
    { date: new Date(2023, 0, 1), value: 20 },
    { date: new Date(2023, 1, 1), value: 60 },
    { date: new Date(2023, 2, 1), value: 70 }
];    const data3 = [
    { date: new Date(2023, 0, 1), value: 40 },
    { date: new Date(2023, 1, 1), value: 30 },
    { date: new Date(2023, 2, 1), value: 90 }
];

/**
 * Initializes the SVG element and defines the margin and dimensions.
 * @returns {Object} Contains the SVG element and its dimensions.
 */
function initializeSVG() {
    const container = document.getElementById("eval-graph");
    const margin = { top: 5, right: 10, bottom: 45, left: 25 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom;
    const svg = d3.select("#eval-graph")
        .append("svg")
        .attr("width", container.clientWidth)
        .attr("height", container.clientHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
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
        .range([0, width]);    const y = d3.scaleLinear()
        .domain([0, d3.max(data.flat(), d => d.value)])
        .range([height, 0]);
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
        .call(d3.axisLeft(y));
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
            d3.select(this).attr("stroke-width", 5);
            tooltip.transition()
                .duration(200)
                .style("opacity", 0.9);
        })
        .on("mousemove", function(event) {
            const [mouseX, mouseY] = d3.pointer(event);
            const xm = x.invert(mouseX);
    const ym = y.invert(mouseY);
            tooltip.html(`Date: ${d3.timeFormat("%B %d, %Y")(xm)}<br>Value: ${ym.toFixed(2)}`)
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
        .attr("fill", (d, i) => colors[i]);
    legend.append("text")
        .attr("x", width - 24)
        .attr("y", 9.5)
        .attr("dy", "0.32em")
        .attr("fill", "white")
        .text(d => d);
}

/**
 * Main function to add the evaluation graph to the page.
 * @param {Array} dataSets - Array of data sets to be plotted.
 * TODO do budoucna mu dát jenom název Pulsaru nebo tak něco a on si už data posbírá fetchem
 */
function addEvalGraph(dataSets) {
    const labels = ["Mean Slowdown", "Bounded Slowdown", "Response Time"];
    const colors = ["rgb(42, 157, 143)", "	rgb(165, 56, 96)", "rgb(114, 9, 183)"];    const { svg, width, height } = initializeSVG();
    const { x, y } = createScales(dataSets, width, height);
    appendAxes(svg, x, y, height);
    addGridLines(svg, x, y, width, height);
    drawLines(svg, dataSets, x, y, colors);
    addInteractivity(svg, x, y);
    drawLegend(svg, width, labels, colors);
}
