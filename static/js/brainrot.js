document.addEventListener("DOMContentLoaded", () => {
  const brainrotLink = document.getElementById("brainrot-link");
  const brainrotText = document.getElementById("brainrot-text");
  const brainrotDiv = document.querySelector(".brainrot");
  let clickedOnce = false;

  // Show text when clicked on the button
  brainrotLink.addEventListener("click", (event) => {
    event.stopPropagation(); // Prevent the click from propagating to the document
    if (!clickedOnce) {
      brainrotText.classList.remove("hidden"); // Show the text
      clickedOnce = true;
    } else {
      window.location.href = "/brainrot"; // Redirect to /brainrot page
    }
  });

  // Close text when clicking outside of the .brainrot div
  document.addEventListener("click", (event) => {
    if (!brainrotDiv.contains(event.target)) {
      brainrotText.classList.add("hidden"); // Hide the text
      clickedOnce = false;
    }
  });
});
