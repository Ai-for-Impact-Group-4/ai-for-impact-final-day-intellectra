// style.js

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropArea = document.getElementById("dropArea");
    const fileInput = document.getElementById("fileInput");
    const previewImage = document.getElementById('previewImage');
    const analyzeButton = document.getElementById('analyzeButton');
    const resultsDiv = document.getElementById('results');

    // --- Drag & Drop Event Listeners ---
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault(); // Prevent default to allow drop
        dropArea.classList.add("dragover"); // Add visual feedback for dragover
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragover"); // Remove visual feedback
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragover");
        const file = e.dataTransfer.files[0]; // Get the first file dropped
        handleFile(file); // Process the dropped file
    });

    // --- Click to Select File Input Listener ---
    // Make the dropArea clickable to open the file input
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Handle file selection via the hidden input
    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        handleFile(file); // Process the selected file
    });

    // --- Function to Handle File (from drop or select) ---
    const handleFile = (file) => {
        if (!file) {
            resultsDiv.innerHTML = '<p style="color: red;">No file selected or dropped.</p>';
            previewImage.style.display = 'none';
            return;
        }

        // Display the selected/dropped file's name (optional, for debugging/user feedback)
        // console.log("File received:", file.name);

        // Show image preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.style.display = 'block';
        };
        reader.readAsDataURL(file); // Read file as Data URL (Base64)

        // Clear previous results when a new image is loaded
        resultsDiv.innerHTML = '';
    };

    // --- Analyze Button Event Listener ---
    analyzeButton.addEventListener('click', async () => {
        const file = fileInput.files[0]; // Get the currently selected file

        if (!file) {
            resultsDiv.innerHTML = '<p style="color: red;">Please select or drop an image first to analyze.</p>';
            return;
        }

        resultsDiv.innerHTML = '<p>Analyzing image... Please wait.</p>';
        // Optionally hide preview during analysis if you want, or show a spinner over it
        // previewImage.style.display = 'none';

        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64String = reader.result.split(',')[1]; // Extract Base64 part

            try {
                const response = await fetch('http://localhost:8000/predict_ewaste', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: base64String }),
                });

                if (!response.ok) {
                    const errorData = await response.json(); // Attempt to read error message from backend
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log("Backend response:", data);

                if (data.status === 'success') {
                    let htmlContent = `<h2>Analysis Result:</h2>`;
                    if (data.primary_ewaste_type) {
                        htmlContent += `<p><strong>Primary E-waste Type Detected:</strong> ${data.primary_ewaste_type}</p>`;

                        // Fetch hazard information for the primary e-waste type
                        const hazardResponse = await fetch(`http://localhost:8000/hazards/${encodeURIComponent(data.primary_ewaste_type)}`);
                        if (hazardResponse.ok) {
                            const hazardData = await hazardResponse.json();
                            htmlContent += `<p><strong>Hazards:</strong> ${hazardData.hazards}</p>`;
                        } else {
                            htmlContent += `<p><em>Could not fetch hazard information for ${data.primary_ewaste_type}.</em></p>`;
                        }
                    }

                    if (data.detections && data.detections.length > 0) {
                        htmlContent += `<h3>All Detections:</h3><ul>`;
                        data.detections.forEach(detection => {
                            htmlContent += `<li>${detection.class_name} (Confidence: ${Math.round(detection.confidence * 100)}%)</li>`;
                        });
                        htmlContent += `</ul>`;
                    } else if (!data.primary_ewaste_type) { // If no primary type and no specific detections
                        htmlContent += `<p>No specific e-waste detected in the image.</p>`;
                        // Optionally fetch general info for "no e-waste detected" if your backend supports it
                        const noEwasteHazardResponse = await fetch(`http://localhost:8000/hazards/${encodeURIComponent('No E-Waste Detected')}`);
                        if (noEwasteHazardResponse.ok) {
                            const noEwasteHazardData = await noEwasteHazardResponse.json();
                            htmlContent += `<p>${noEwasteHazardData.hazards}</p>`;
                        }
                    }

                    resultsDiv.innerHTML = htmlContent;

                    // Dummy recycling stores (You can expand this based on your needs)
                    resultsDiv.innerHTML += `<h3>Nearby Recycling / Selling Stores (Mock Data):</h3>
                        <ul>
                            <li>GreenTech Recycle Hub - 123 Eco Lane</li>
                            <li>E-Waste Solutions - 456 Circuit Street</li>
                            <li>Local Scrap Dealer - Near Industrial Area</li>
                        </ul>`;

                } else {
                    resultsDiv.innerHTML = `<p style="color: red;">Error: ${data.message || 'Unknown error during analysis.'}</p>`;
                }

            } catch (error) {
                console.error("Error sending request to backend:", error);
                resultsDiv.innerHTML = `<p style="color: red;">Failed to connect to the analysis server or an error occurred. Please ensure the backend is running at http://localhost:8000. Error: ${error.message}</p>`;
            }
        };
        reader.readAsDataURL(file); // This triggers onloadend
    });
});