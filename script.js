document.addEventListener("DOMContentLoaded", function () {
    const aqiValueElement = document.getElementById("aqi-value");
    const fillElement = document.getElementById("fill");
    const maskFullElement = document.getElementById("mask-full");

    // Fetch the air quality data
    fetch('https://api.waqi.info/feed/here/?token=03fb00810b1773ffd525c9a786d71aed176d4201')
        .then(response => response.json())
        .then(data => {
            const aqi = data.data.aqi;
            updateProgress(aqi);
        })
        .catch(error => {
            console.error('Error fetching AQI:', error);
        });

    // Function to update the progress circle based on AQI
    function updateProgress(aqi) {
        const angle = Math.min((aqi / 500) * 360, 360); // AQI max is 500
        aqiValueElement.textContent = aqi;

        if (angle <= 180) {
            fillElement.style.transform = `rotate(${angle}deg)`;
            maskFullElement.style.backgroundColor = "transparent";
        } else {
            fillElement.style.transform = "rotate(180deg)";
            maskFullElement.style.backgroundColor = "#4caf50"; // Same as the fill color
            document.querySelector('.mask.half .fill').style.transform = `rotate(${angle - 180}deg)`;
        }

        // Change progress color based on AQI levels
        if (aqi <= 50) {
            fillElement.style.backgroundColor = "#4caf50"; // Green - Good
        } else if (aqi <= 100) {
            fillElement.style.backgroundColor = "#ffeb3b"; // Yellow - Moderate
        } else if (aqi <= 150) {
            fillElement.style.backgroundColor = "#ff9800"; // Orange - Unhealthy for Sensitive Groups
        } else if (aqi <= 200) {
            fillElement.style.backgroundColor = "#f44336"; // Red - Unhealthy
        } else if (aqi <= 300) {
            fillElement.style.backgroundColor = "#9c27b0"; // Purple - Very Unhealthy
        } else {
            fillElement.style.backgroundColor = "#673ab7"; // Maroon - Hazardous
        }
    }
});
