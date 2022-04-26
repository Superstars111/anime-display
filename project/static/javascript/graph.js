// Taken from https://www.digitalocean.com/community/tutorials/getting-started-with-data-visualization-using-javascript-and-the-d3-library
// And from https://www.chartjs.org/docs/latest/samples/other-charts/scatter.html
// And from http://www.java2s.com/example/javascript/chart.js/chartjs-to-create-scatter-chart.html
// let dataArray = [23, 13, 24, 42, 75, 61, 54, 15, 68];
//
// let svg = d3.select("body").append("svg")
//             .attr("height", "100%")
//             .attr("width", "100%");
//
// svg.selectAll("rect")
//     .data(dataArray)
//     .enter().append("rect")
//       .attr("class", "bar")
//       .attr("height", function (d, i) {return (d * 10)})
//       .attr("width", "40")
//       .attr("x", function (d, i) {return (i * 60) + 25})
//       .attr("y", function (d, i) {return 800 - (d * 10)})
//
// svg.selectAll("text")
//     .data(dataArray)
//     .enter().append("text")
//       .text(function (d) {return d;})
//       .attr("x", function (d, i) {return (i * 60) + 36})
//       .attr("y", function (d, i) {return 790 - (d * 10)})

// import colorLib from '@kurkle/color';
// import {DateTime} from 'luxon';
// import 'chartjs-adapter-luxon';
// import {valueOrDefault} from '../../dist/helpers.esm';

// var _seed = Date.now();
//
// const config = {
//   type: 'scatter',
//   data: data,
//   options: {
//     responsive: true,
//     // plugins: {
//     //   legend: {
//     //     position: 'top',
//     //   },
//       title: {
//         display: true,
//         text: 'Chart.js Scatter Chart'
//       }
//     }
//   // },
// };
//
// // export function transparentize(value, opacity) {
// //   var alpha = opacity === undefined ? 0.5 : 1 - opacity;
// //   return colorLib(value).alpha(alpha).rgbString();
// // }
//
// const MONTHS = [
//   'January',
//   'February',
//   'March',
//   'April',
//   'May',
//   'June',
//   'July',
//   'August',
//   'September',
//   'October',
//   'November',
//   'December',
// ];
//
// export function months(config) {
//   var cfg = config || {};
//   var count = cfg.count || 12;
//   var section = cfg.section;
//   var values = [];
//   var i, value;
//
//   for (i = 0; i < count; ++i) {
//     value = MONTHS[Math.ceil(i) % 12];
//     values.push(value.substring(0, section));
//   }
//
//   return values;
// }
//
// export function rand(min, max) {
//   min = 2;
//   max = 4;
//   _seed = (_seed * 9301 + 49297) % 233280;
//   return min + (_seed / 233280) * (max - min);
// }
//
// export function bubbles(config) {
//   return this.points(config).map(pt => {
//     pt.r = this.rand(config.rmin, config.rmax);
//     return pt;
//   });
// }
//
// const DATA_COUNT = 7;
// const NUMBER_CFG = {count: DATA_COUNT, rmin: 1, rmax: 1, min: 0, max: 100};
//
// export const CHART_COLORS = {
//   red: 'rgb(255, 99, 132)',
//   orange: 'rgb(255, 159, 64)',
//   yellow: 'rgb(255, 205, 86)',
//   green: 'rgb(75, 192, 192)',
//   blue: 'rgb(54, 162, 235)',
//   purple: 'rgb(153, 102, 255)',
//   grey: 'rgb(201, 203, 207)'
// };
//
// const labels = months({count: 7});
// const data = {
//   labels: labels,
//   datasets: [
//     {
//       label: 'Dataset 1',
//       data: bubbles(NUMBER_CFG),
//       borderColor: CHART_COLORS.red,
//       // backgroundColor: transparentize(CHART_COLORS.red, 0.5),
//     },
//     // {
//     //   label: 'Dataset 2',
//     //   data: Utils.bubbles(NUMBER_CFG),
//     //   borderColor: Utils.CHART_COLORS.orange,
//     //   backgroundColor: Utils.transparentize(Utils.CHART_COLORS.orange, 0.5),
//     // }
//   ]
// };

// const actions = [
//   {
//     name: 'Randomize',
//     handler(chart) {
//       chart.data.datasets.forEach(dataset => {
//         dataset.data = Utils.bubbles({count: chart.data.labels.length, rmin: 1, rmax: 1, min: 0, max: 100});
//       });
//       chart.update();
//     }
//   },
//   {
//     name: 'Add Dataset',
//     handler(chart) {
//       const data = chart.data;
//       const dsColor = Utils.namedColor(chart.data.datasets.length);
//       const newDataset = {
//         label: 'Dataset ' + (data.datasets.length + 1),
//         backgroundColor: Utils.transparentize(dsColor, 0.5),
//         borderColor: dsColor,
//         data: Utils.bubbles({count: data.labels.length, rmin: 1, rmax: 1, min: 0, max: 100}),
//       };
//       chart.data.datasets.push(newDataset);
//       chart.update();
//     }
//   },
//   {
//     name: 'Add Data',
//     handler(chart) {
//       const data = chart.data;
//       if (data.datasets.length > 0) {
//
//         for (let index = 0; index < data.datasets.length; ++index) {
//           data.datasets[index].data.push(Utils.bubbles({count: 1, rmin: 1, rmax: 1, min: 0, max: 100})[0]);
//         }
//
//         chart.update();
//       }
//     }
//   },
//   {
//     name: 'Remove Dataset',
//     handler(chart) {
//       chart.data.datasets.pop();
//       chart.update();
//     }
//   },
//   {
//     name: 'Remove Data',
//     handler(chart) {
//       chart.data.labels.splice(-1, 1); // remove the label first
//
//       chart.data.datasets.forEach(dataset => {
//         dataset.data.pop();
//       });
//
//       chart.update();
//     }
//   }
// ];

// let data_test = [
//   {x: 23, y: 40},
//   {x: 32, y: -23},
//   {x: -30, y: -10},
//   {x: 2, y: 3},
//   {x: -50, y: -50},
//   {x: 50, y: 50}
// ];

let graph = document.getElementById("test_graph")

let raw_data = graph.dataset.ratings;

let data_test = JSON.parse(raw_data)

let ctx = document.getElementById("test_graph").getContext("2d");

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
    // responsive: false,
    showLines: true,
    aspectRatio: 1,
    // scales: {
    //   yAxes: [{
    //     ticks: {
    //       min: 28,
    //       max: 40,
    //     }
    //   }],
    // },
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

// from https://css-tricks.com/value-bubbles-for-range-inputs/

const allRanges = document.querySelectorAll(".range-wrap");
allRanges.forEach(wrap => {
  const range = wrap.querySelector(".slider");
  const bubble = wrap.querySelector(".bubble");

  range.addEventListener("input", () => {
    setBubble(range, bubble);
  });
  setBubble(range, bubble);
});

function setBubble(range, bubble) {
  const val = range.value;
  const min = range.min ? range.min : 0;
  const max = range.max ? range.max : 100;
  const newVal = Number(((val - min) * 100) / (max - min));
  bubble.innerHTML = val;

  // Sorta magic numbers based on size of the native UI thumb
  bubble.style.left = `calc(${newVal}% + (${8 - newVal * 0.15}px))`;
}

// var canvas = document.getElementById('canvas');
// var ctx = canvas.getContext('2d');

// var myChart = new Chart(ctx, {
//    type: 'line',
//    data: {
//       labels: ["2010", "2011", "2012", "2013"],
//       datasets: [{
//          label: 'Dataset 1',
//          data: [150, 200, 250, 150],
//          color: "#878BB6",
//       }, {
//          label: 'Dataset 2',
//          data: [250, 100, 150, 10],
//          color: "#4ACAB4",
//       }]
//    }
// });