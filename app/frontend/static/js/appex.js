// Function to generate sample data with fluctuations
function generateData() {
  let data = [];
  let val = 30;
  const date = new Date("2023-01-01");

  for (let i = 0; i < 365; i++) {
    // 1-year timeline
    val += (Math.random() - 0.5) * 4; // Random fluctuations
    val = Math.max(25, Math.min(45, val)); // Keep between 25-45
    data.push({
      x: new Date(date),
      y: val.toFixed(2),
    });
    date.setDate(date.getDate() + 1);
  }
  return data;
}

// ApexCharts Configuration
var options = {
  series: [
    {
      name: "Metric",
      data: generateData(),
    },
  ],
  chart: {
    type: "area",
    height: 500,
    toolbar: {
      show: true,
      tools: {
        zoom: true,
        zoomin: true,
        zoomout: true,
        reset: true,
      },
    },
    zoom: {
      enabled: true,
      type: "x",
      autoScaleYaxis: true,
    },
  },
  colors: ["#4680FF"],
  dataLabels: { enabled: false },
  stroke: { curve: "smooth", width: 2 },
  fill: {
    type: "gradient",
    gradient: {
      shadeIntensity: 0.9,
      opacityFrom: 0.7,
      opacityTo: 0.2,
      stops: [0, 100],
    },
  },
  xaxis: {
    type: "datetime",
    labels: {
      format: "MMM yy",
    },
  },
  yaxis: {
    min: 20,
    max: 50,
    tickAmount: 8,
    labels: {
      formatter: function (val) {
        return val.toFixed(0);
      },
    },
  },
  grid: {
    borderColor: "#CCCCCC42",
    strokeDashArray: 3,
    yaxis: { lines: { show: true } },
    xaxis: { lines: { show: false } },
  },
  tooltip: {
    x: { format: "dd MMM yyyy" },
  },
  annotations: {
    points: [
      {
        x: new Date("2023-03-15").getTime(),
        y: 45,
        marker: { size: 8, fillColor: "#ff0000" },
        label: { text: "Peak", borderColor: "#ff0000" },
      },
      {
        x: new Date("2023-08-01").getTime(),
        y: 25,
        marker: { size: 8, fillColor: "#00ff00" },
        label: { text: "Trough", borderColor: "#00ff00" },
      },
    ],
  },
};

// Render the chart
var chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();
