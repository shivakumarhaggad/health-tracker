const metricsData = [
    {% for metric in metrics %}
      {
        "timestamp": "{{ metric.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}",
        "heart_rate": {{ metric.heart_rate }},
        "blood_pressure_systolic": {{ metric.blood_pressure_systolic }},
        "blood_pressure_diastolic": {{ metric.blood_pressure_diastolic }},
        "calorie_count": {{ metric.calorie_count }}
      },
    {% endfor %}
  ];

  const metricsHistoryContainer = document.getElementById("metrics-history");

  if (metricsData && metricsData.length > 0) {
    metricsData.forEach((metric) => {
      const metricItem = document.createElement("div");
      metricItem.className = "metric-item";

      metricItem.innerHTML = `
        <p><strong>Date:</strong> ${metric.timestamp}</p>
        <p><strong>Heart Rate:</strong> ${metric.heart_rate} BPM</p>
        <p><strong>Blood Pressure:</strong> ${metric.blood_pressure_systolic}/${metric.blood_pressure_diastolic}</p>
        <p><strong>Calorie Count:</strong> ${metric.calorie_count}</p>
      `;

      metricsHistoryContainer.appendChild(metricItem);
    });
  } else {
    metricsHistoryContainer.innerHTML = "<p>No metrics recorded yet.</p>";
  }