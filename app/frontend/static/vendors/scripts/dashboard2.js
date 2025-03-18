$(document).ready(function () {
  $(".knob").knob();
  function animateKnob(selector, targetValue) {
    $({ value: 0 }).animate(
      { value: targetValue },
      {
        duration: 2000,
        easing: "swing",
        step: function (now) {
          $(selector).val(Math.ceil(now)).trigger("change");
        },
      },
    );
  }
  animateKnob(".knob1", 100);
  animateKnob(".knob2", 75);
  animateKnob(".knob3", 35);
  animateKnob(".knob4", 70);

  // 1. Employee Attendance Rate (Last 30 Days)
  const topEmployeesCtx = document
    .getElementById("topEmployeesChart")
    .getContext("2d");
  fetch("/api/productivity/attendance")
    .then((response) => response.json())
    .then((data) => {
      new Chart(topEmployeesCtx, {
        type: "bar",
        data: {
          labels: data.employee_ids.map((id) => `Employee ${id}`),
          datasets: [
            {
              label: "Attendance Rate (%)",
              data: data.rates,
              backgroundColor: "#1E88E5",
              borderColor: "#1E88E5",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          scales: {
            x: { title: { display: true, text: "Employee" } },
            y: {
              min: 0,
              max: 100,
              title: { display: true, text: "Attendance Rate (%)" },
            },
          },
          plugins: {
            title: {
              display: true,
              text: "Employee Attendance Rate (Last 30 Days)",
            },
          },
        },
      });
    });

  // 2. Average Daily Productive Hours (Last 7 Days)
  const performanceCtx = document
    .getElementById("performanceChart")
    .getContext("2d");
  fetch("/api/productivity/performance")
    .then((response) => response.json())
    .then((data) => {
      new Chart(performanceCtx, {
        type: "bar",
        data: {
          labels: data.employee_ids.map((id) => `Employee ${id}`),
          datasets: [
            {
              label: "Productive Hours",
              data: data.hours,
              backgroundColor: "#43A047",
              borderColor: "#43A047",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          indexAxis: "y",
          scales: {
            x: {
              min: 0,
              max: 8,
              title: { display: true, text: "Avg Hours/Day" },
            },
            y: { title: { display: true, text: "Employee" } },
          },
          plugins: {
            title: {
              display: true,
              text: "Average Daily Productive Hours (Last 7 Days)",
            },
          },
        },
      });
    });

  // 3. Daily Eye Closure Duration (Last 7 Days)
  let employeeId =
    document.cookie
      .split("; ")
      .find((row) => row.startsWith("employee_id="))
      ?.split("=")[1] || 2;
  fetch(`/api/productivity/metric-trends?employee_id=${employeeId}`)
    .then((response) => response.json())
    .then((data) => {
      var metricOptions = {
        series: [{ name: "Eye Closure", data: data.map((d) => d.y) }],
        chart: { type: "area", height: 400 },
        colors: ["#F4511E"],
        stroke: { curve: "smooth", width: 2 },
        fill: {
          type: "gradient",
          gradient: { opacityFrom: 0.6, opacityTo: 0.1 },
        },
        xaxis: {
          categories: data.map((d) => d.x),
          type: "datetime",
          labels: { format: "dd MMM" },
          title: { text: "Date" },
        },
        yaxis: { min: 0, max: 15, title: { text: "Minutes" } },
        title: {
          text: "Daily Eye Closure Duration (Last 7 Days)",
          align: "center",
        },
      };
      new ApexCharts(
        document.querySelector("#metric-chart"),
        metricOptions,
      ).render();
    });

  // 4. Employee Activity Comparison (Last 7 Days)
  fetch(`/api/productivity/activity-comparison?employee_id=${employeeId}`)
    .then((response) => response.json())
    .then((data) => {
      var activityOptions = {
        series: [
          { name: "Recognized Time", data: data.recognized },
          { name: "Inactive Time", data: data.eye_closed },
        ],
        chart: { type: "bar", height: 350 },
        plotOptions: { bar: { columnWidth: "55%" } },
        colors: ["#1976D2", "#D81B60"],
        xaxis: {
          categories: data.dates,
          title: { text: "Date" },
        },
        yaxis: { min: 0, max: 60, title: { text: "Duration (Minutes)" } },
        title: {
          text: "Employee Activity Comparison (Last 7 Days)",
          align: "center",
        },
      };
      new ApexCharts(
        document.querySelector("#ai-performance-chart"),
        activityOptions,
      ).render();
    });

  // 5. Employee Time Allocation (Last 7 Days)
  fetch(`/api/productivity/performance-distribution?employee_id=${employeeId}`)
    .then((response) => response.json())
    .then((data) => {
      var donutOptions = {
        series: data,
        chart: { type: "donut", height: 350 },
        colors: ["#0288D1", "#D81B60", "#7CB342", "#455A64"],
        labels: ["Recognized", "Eye Closed", "Other", "Productive"],
        dataLabels: { formatter: (val) => `${val.toFixed(1)}%` },
        legend: { position: "bottom" },
        title: {
          text: "Employee Time Allocation (Last 7 Days)",
          align: "center",
        },
      };
      new ApexCharts(
        document.querySelector("#donut-chart"),
        donutOptions,
      ).render();
    });
});
