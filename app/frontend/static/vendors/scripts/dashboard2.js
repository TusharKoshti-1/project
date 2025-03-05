


$(document).ready(function () {
	$(".knob").knob(); // Initialize all knob elements
	
	// Animate each knob individually
	function animateKnob(selector, targetValue) {
		$({ value: 0 }).animate({ value: targetValue }, {
			duration: 2000,
			easing: "swing",
			step: function (now) {
				$(selector).val(Math.ceil(now)).trigger("change");
			}
		});
	}

	animateKnob(".knob1", 100);
	animateKnob(".knob2", 75);
	animateKnob(".knob3", 35);
	animateKnob(".knob4", 70);
});

// Attendance Chart
const topEmployeesCtx = document.getElementById('topEmployeesChart').getContext('2d');
new Chart(topEmployeesCtx, {
	type: 'bar',
	data: {
		labels: ['Mayank', 'Tushar', 'Het', 'Bhavya', 'Bhupendra', 'Shubham'],
		datasets: [{
			label: 'Attendance Percentage',
			data: [96.15, 94.44, 92.78, 91.67, 91.67, 90],
			backgroundColor: '#111e88'
		}]
	},
	options: {
		responsive: true,
		scales: {
			x: { beginAtZero: true },
			y: { beginAtZero: true, max: 100 }
		}
	}
});

// Performance Chart
const performanceCtx = document.getElementById('performanceChart').getContext('2d');
new Chart(performanceCtx, {
	type: 'bar',
	data: {
		labels: ['Mayank', 'Tushar', 'Het', 'Bhavya', 'Shubham'],
		datasets: [{
			label: 'Performance Score (%)',
			data: [98, 95, 92, 89, 87],
			backgroundColor: '#111e88',
			borderWidth: 1
		}]
	},
	options: {
		responsive: true,
		maintainAspectRatio: false,
		indexAxis: 'y',
		scales: {
			x: {
				beginAtZero: true,
				max: 100,
				ticks: { stepSize: 10 }
			}
		},
		plugins: {
			legend: { display: false },
			tooltip: {
				callbacks: {
					label: function(tooltipItem) {
						return ` ${tooltipItem.label}: ${tooltipItem.raw}%`;
					}
				}
			}
		}
	}
});

