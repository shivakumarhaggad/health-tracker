document.addEventListener("DOMContentLoaded", function () {
  const healthMetricForm = document.getElementById("health-metric-form");
  const healthTipsContainer = document.getElementById("health-tips");

  // Handle form submission
  healthMetricForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(healthMetricForm);
    const data = Object.fromEntries(formData.entries());

    try {
      const response = await fetch("/api/health-metrics", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error("Failed to submit metrics");
      }

      // Clear form
      healthMetricForm.reset();

      // Load health tips after submission
      loadHealthTips();

      alert("Health metrics submitted successfully!");
    } catch (error) {
      console.error("Error:", error);
      alert("Failed to submit health metrics. Please try again.");
    }
  });

  // Convert text to markdown
  function convertToMarkdown(text) {
    const lines = text.split("\n");
    let markdown = "";
    let inList = false;

    lines.forEach((line) => {
      line = line.trim();

      if (line === "") {
        markdown += "\n";
        inList = false;
      } else if (line.match(/^Based on the provided health metrics/i)) {
        markdown += "# Personalized Health Tips and Recommendations\n\n";
        markdown += line + "\n\n";
      } else if (line.match(/^(Heart Rate|Blood Pressure|Calorie Count):/i)) {
        const [metric, value] = line.split(":");
        markdown += `## ${metric.trim()}: ${value.trim()}\n\n`;
      } else if (line.match(/^\d+\.\s/)) {
        if (!inList) {
          markdown += "\n";
          inList = true;
        }
        markdown += line + "\n";
      } else if (line.match(/^Additional Recommendations$/i)) {
        markdown += "## " + line + "\n\n";
      } else if (line.match(/^By following these personalized/i)) {
        markdown += "\n" + line + "\n";
      } else {
        if (inList) {
          markdown += "\n";
          inList = false;
        }
        markdown += line + "\n";
      }
    });

    return markdown.trim();
  }

  // Load health tips
  async function loadHealthTips() {
    try {
      const response = await fetch("/api/health-tips");
      if (!response.ok) {
        throw new Error("Failed to fetch health tips");
      }

      const data = await response.json();
      const markdownTips = convertToMarkdown(data.health_tips);

      healthTipsContainer.innerHTML = `
            <div class="tips-content">
              <div id="markdown-tips"></div>
              <div class="current-metrics">
                <h3>Current Metrics:</h3>
                <p>Heart Rate: ${data.metrics.heart_rate} BPM</p>
                <p>Blood Pressure: ${data.metrics.blood_pressure} mmHg</p>
                <p>Calorie Count: ${data.metrics.calorie_count} 
                kcal</p>
              </div>
            </div>
          `;

      // Use a markdown rendering library to convert markdown to HTML
      // For this example, we'll use a placeholder function
      document.getElementById("markdown-tips").innerHTML =
        renderMarkdown(markdownTips);
    } catch (error) {
      console.error("Error:", error);
      healthTipsContainer.innerHTML =
        "<p>Unable to load health tips at this time.</p>";
    }
  }

  // Placeholder function for markdown rendering
  function renderMarkdown(markdown) {
    // In a real application, you would use a library like marked or showdown
    // to convert markdown to HTML. For this example, we'll do a simple conversion.
    return markdown
      .replace(/^# (.*$)/gm, "<h1>$1</h1>")
      .replace(/^## (.*$)/gm, "<h2>$1</h2>")
      .replace(/^### (.*$)/gm, "<h3>$1</h3>")
      .replace(/\n\n/g, "<br><br>")
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  }
});
