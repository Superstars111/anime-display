// Update graph data

function updateGraphData() {
  removeData(scatter);
  let new_data = JSON.parse(httpRequest.response);
  addData(scatter, new_data);
}

// const graphButton = document.getElementById("graphButton");
//
// const GBVAR = partial(setVariables, "/graph_test", [graphButton], updateGraphData);
//
// graphButton.onclick = GBVAR;

// Based on https://www.chartjs.org/docs/latest/samples/other-charts/scatter.html
// And on http://www.java2s.com/example/javascript/chart.js/chartjs-to-create-scatter-chart.html

const graph = document.getElementById("display_graph")
const ctx = graph.getContext("2d");
let rawData = graph.dataset.points;
let parsedData = JSON.parse(rawData);

let data = {
    labels: ["A", "B", "C", "D"],
    datasets: [{
      label: "Test Scatter Graph",
      borderColor: 'rgb(255, 99, 132)',
      data: parsedData,
      color: "#878BB6"
    }]};

const options = {
    title: {
      display: true,
      text: "Testing Data"
    },
    showLines: true,
    aspectRatio: 1,
    layout: {
      padding: 0

    },
    scales: {
      y: {
        min: -51,
        max: 51,
        ticks: {
          stepSize: 25,
          display: false
        },
        grid: {
          drawTicks: false
        },
        title: {
          display: true,
          text: "Y Axis",
        }
      },
      x: {
        min: -51,
        max: 51,
        ticks: {
          stepSize: 25,
          display: false
        },
        grid: {
          drawTicks: false,
        },
        title: {
          display: true,
          text: "X Axis"
        }
      },
    },
    elements: {
      point: {
        radius: 5
      }
    }
};

const scatter = new Chart(ctx, {
  type: "scatter",
  data: data,
  options: options
});


function addData(chart, data) {
    // chart.data.labels.push(label);  To reinstate, add "label" arg back to function
    chart.data.datasets.forEach((dataset) => {
      for (let i = 0; i < data.length; i++) {
        dataset.data.push(data[i]);
      }
    });
    chart.update();
}

function removeData(chart) {
    chart.data.labels.pop();
    chart.data.datasets.forEach((dataset) => {
      while (dataset.data.length) {
        dataset.data.pop();
      }
    });
    chart.update();
}
