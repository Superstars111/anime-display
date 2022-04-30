// Taken from https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX/Getting_Started

// Update graph data
let httpRequest;
document.getElementById("ratingButton").onclick = function () {
  let change = document.getElementById("ratingButton").value;
  makeRequest("/graph_test", change);
  // TODO: Make endpoint dynamic
};

function makeRequest(url, change) {
  httpRequest = new XMLHttpRequest();

  if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }

  httpRequest.open("GET", url + `?change=${change}`);
  httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); //Don't understand what this header means
  httpRequest.onreadystatechange = sendUpdate;
  httpRequest.send();
}

function sendUpdate() {
  if (httpRequest.readyState === 4) {
    if (httpRequest.status === 200) {
      removeData(scatter);
      let new_data = JSON.parse(httpRequest.response)
      addData(scatter, new_data);
    }
    else {
      console.log("Status: " + httpRequest.status);
    }
  }
}

// Taken from https://www.chartjs.org/docs/latest/samples/other-charts/scatter.html
// And from http://www.java2s.com/example/javascript/chart.js/chartjs-to-create-scatter-chart.html

let graph = document.getElementById("display_graph")
let ctx = graph.getContext("2d");
let raw_data = graph.dataset.points;
let data_test = JSON.parse(raw_data)

let data = {
    labels: ["A", "B", "C", "D"],
    datasets: [{
      label: "Test Scatter Graph",
      borderColor: 'rgb(255, 99, 132)',
      data: data_test,
      color: "#878BB6"
    }]};

let options = {
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

let scatter = new Chart(ctx, {
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
