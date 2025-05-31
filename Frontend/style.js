// style.js

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const dropArea = document.getElementById("dropArea");
    const fileInput = document.getElementById("fileInput");
    const imageCanvas = document.getElementById('imageCanvas'); // Reference to the canvas
    const ctx = imageCanvas.getContext('2d'); // 2D rendering context
    const analyzeButton = document.getElementById('analyzeButton');
    const resultsDiv = document.getElementById('results');

    let originalImage = new Image(); // Store the original image to redraw

    // --- Drag & Drop Event Listeners ---
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragover");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragover");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragover");
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // --- Click to Select File Input Listener ---
    dropArea.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    // --- Function to Handle File (draws on canvas) ---
    const handleFile = (file) => {
        if (!file) {
            resultsDiv.innerHTML = '<p style="color: red;">No file selected or dropped.</p>';
            imageCanvas.style.display = 'none'; // Hide canvas if no file
            return;
        }

        resultsDiv.innerHTML = ''; // Clear previous results
        
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImage.onload = () => {
                // Set canvas dimensions to match image
                imageCanvas.width = originalImage.width;
                imageCanvas.height = originalImage.height;

                // Make sure canvas fits within max-width of its container
                // This scales the canvas for display, but drawing occurs on its intrinsic dimensions
                const maxWidth = imageCanvas.parentElement.clientWidth; // Get parent width
                if (imageCanvas.width > maxWidth) {
                    imageCanvas.style.width = '100%';
                    imageCanvas.style.height = 'auto';
                } else {
                    imageCanvas.style.width = `${imageCanvas.width}px`;
                    imageCanvas.style.height = `${imageCanvas.height}px`;
                }

                ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height); // Clear any previous drawings
                ctx.drawImage(originalImage, 0, 0); // Draw the image on the canvas
                imageCanvas.style.display = 'block'; // Show the canvas
            };
            originalImage.src = e.target.result; // Set image source, which triggers originalImage.onload
        };
        reader.readAsDataURL(file);
    };

    // --- Analyze Button Event Listener ---
    analyzeButton.addEventListener('click', async () => {
        const file = fileInput.files[0];

        if (!file) {
            resultsDiv.innerHTML = '<p style="color: red;">Please select or drop an image first to analyze.</p>';
            return;
        }

        resultsDiv.innerHTML = '<p>Analyzing image... Please wait.</p>';
        // Clear previous drawings on the canvas, keeping the image
        ctx.clearRect(0, 0, imageCanvas.width, imageCanvas.height);
        ctx.drawImage(originalImage, 0, 0); // Redraw original image

        const reader = new FileReader();
        reader.onloadend = async () => {
            const base64String = reader.result.split(',')[1];

            try {
                const response = await fetch('http://localhost:8000/predict_ewaste', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: base64String }),
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log("Backend response:", data);

                if (data.status === 'success') {
                    let htmlContent = `<h2>Analysis Result:</h2>`;
                    let primaryEwasteType = data.primary_ewaste_type;

                    if (primaryEwasteType && primaryEwasteType !== "no e-waste detected") {
                         htmlContent += `<p><strong>Primary E-waste Type Detected:</strong> ${primaryEwasteType}</p>`;
                         const hazardResponse = await fetch(`http://localhost:8000/hazards/${encodeURIComponent(primaryEwasteType)}`);
                         if (hazardResponse.ok) {
                             const hazardData = await hazardResponse.json();
                             htmlContent += `<p><strong>Hazards:</strong> ${hazardData.hazards}</p>`;
                         } else {
                             htmlContent += `<p><em>Could not fetch hazard information for ${primaryEwasteType}.</em></p>`;
                         }
                    } else {
                        htmlContent += `<p>No specific e-waste detected in the image.</p>`;
                        const noEwasteHazardResponse = await fetch(`http://localhost:8000/hazards/${encodeURIComponent('No E-Waste Detected')}`);
                        if (noEwasteHazardResponse.ok) {
                            const noEwasteHazardData = await noEwasteHazardResponse.json();
                            htmlContent += `<p>${noEwasteHazardData.hazards}</p>`;
                        }
                    }


                    if (data.detections && data.detections.length > 0) {
                        htmlContent += `<h3>All Detections:</h3><ul>`;
                        data.detections.forEach(detection => {
                            htmlContent += `<li>${detection.class_name} (Confidence: ${Math.round(detection.confidence * 100)}%)</li>`;
                            
                            // --- DRAW BOUNDING BOX ON CANVAS ---
                            const [x1, y1, x2, y2] = detection.bbox;
                            const confidence = detection.confidence;
                            const className = detection.class_name;

                            // Scale factors (if canvas displayed width/height differ from intrinsic width/height)
                            const scaleX = imageCanvas.width / originalImage.width;
                            const scaleY = imageCanvas.height / originalImage.height;

                            ctx.beginPath();
                            ctx.rect(x1 * scaleX, y1 * scaleY, (x2 - x1) * scaleX, (y2 - y1) * scaleY);
                            ctx.lineWidth = 2;
                            ctx.strokeStyle = '#00FF00'; // Green color for bounding box
                            ctx.stroke();

                            // Draw label
                            ctx.fillStyle = '#00FF00';
                            ctx.font = '16px Arial';
                            const label = `${className} (${(confidence * 100).toFixed(1)}%)`;
                            // Position text slightly above the box, adjusting for potential canvas scaling
                            ctx.fillText(label, x1 * scaleX, (y1 * scaleY) - 5);
                        });
                        htmlContent += `</ul>`;
                    } else {
                        htmlContent += `<p>No specific e-waste detected.</p>`;
                        // If no specific e-waste, ensure primary_ewaste_type reflects this
                        primaryEwasteType = 'no e-waste detected'; 
                    }

                    resultsDiv.innerHTML = htmlContent;

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
                resultsDiv.innerHTML = `<p style="color: red;">Failed to connect to the analysis server. Please ensure the backend is running. Error: ${error.message}</p>`;
            }
        };
        reader.readAsDataURL(file);
    });
});