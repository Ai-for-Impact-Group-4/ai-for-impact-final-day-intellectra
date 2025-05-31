# main.py
import base64
import io
import os
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO # Make sure ultralytics is installed and supports your YOLO version

# --- FastAPI App Initialization ---
app = FastAPI(
    title="E-waste YOLO Prediction API",
    description="API for E-waste detection using a custom YOLO model.",
    version="1.0.0"
)

# --- CORS Configuration ---
# This is crucial for your frontend (running on a different port/origin)
# to be able to communicate with this backend API.
# In production, you should replace "*" with the specific origin(s) of your frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development purposes.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.).
    allow_headers=["*"],  # Allows all headers.
)

# --- Model Loading ---
# CUSTOM ADDITION 1:
# Ensure this path points to your trained YOLO model file.
# Your model file (e.g., yolov8s_ewaste.pt) should be inside the 'models' directory
# relative to this main.py file (e.g., backend/models/yolov8s_ewaste.pt).
MODEL_PATH = os.path.join("models", "D:\CODES\ai-for-impact-final-day-intellectra\backend\models\best (8).pt")

# Initialize model variable
model = None

# Load the YOLO model when the FastAPI application starts up.
# This ensures the model is loaded only once, improving performance.
@app.on_event("startup")
async def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: YOLO model not found at: {MODEL_PATH}. Please ensure your model is in the 'models' directory.")
        # In a production environment, you might want to raise an exception
        # or exit the application if the model is critical and missing.
        # For a hackathon MVP, we'll allow the app to start but predictions will fail.
        return

    try:
        model = YOLO(MODEL_PATH)
        print(f"YOLO model loaded successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to load YOLO model from {MODEL_PATH}: {e}")
        model = None # Ensure model is None if loading fails

# --- Dummy E-waste Info Map ---
# CUSTOM ADDITION 2:
# IMPORTANT: The keys in this dictionary (e.g., 'laptop', 'smartphone')
# MUST EXACTLY MATCH the class names that your trained YOLO model outputs.
# If your model outputs 'mobile_phone' instead of 'smartphone', adjust accordingly.
#'adapter', 'battery', 'cable', 'memory', 'pcb', 'phone', 'remote
ewaste_info_map = {
    'cable': {
        'hazards': 'Laptops contain heavy metals like lead, mercury, and cadmium, and brominated flame retardants. These are highly toxic if improperly disposed of and can pollute soil and water.'
    },
    'phone': {
        'hazards': 'Smartphones contain lead, mercury, cadmium, arsenic, and brominated flame retardants. These substances can leach into soil and water, posing significant health risks.'
    },
    'memory': {
        'hazards': 'Old CRT TVs contain significant amounts of lead in their cathode ray tubes. Newer flat-screen TVs can contain mercury in backlights and other hazardous materials like lead and cadmium.'
    },
    'battery': {
        'hazards': 'Batteries (especially lithium-ion and nickel-cadmium) contain heavy metals like lead, cadmium, mercury, and lithium, which are highly toxic. They also pose fire risks if damaged.'
    },
    'adapter': {
        'hazards': 'Adapters primarily contain plastics, copper, and some trace amounts of hazardous materials. While less acutely toxic than other e-waste, they contribute to landfill waste and resource depletion.'
    },
    'remote': {
        'hazards': 'Printers contain plastics, metals, and residual ink/toner. Toner can be a respiratory irritant, and some components may contain lead or cadmium. Ink cartridges are also a significant waste concern.'
    },
    'pcb': { # Example: If your model detects 'circuit_board'
        'hazards': 'Circuit boards are highly complex and contain a wide array of hazardous materials including lead, mercury, cadmium, beryllium, and brominated flame retardants. They are very hazardous if not recycled properly.'
    },
    'other_ewaste': { # A generic class for any e-waste not specifically categorized by your model
        'hazards': 'Generic e-waste can contain a mix of plastics, metals, and various hazardous substances depending on the specific components. Proper disposal is crucial to prevent environmental contamination.'
    },
    'no e-waste detected': { # Special entry for when no e-waste is found
        'hazards': 'This item was not identified as electronic waste. Therefore, specific e-waste hazards do not apply.'
    }
    # Add more entries here if your YOLO model has other specific e-waste classes.
}


# --- API Endpoints ---

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the E-waste YOLO Prediction API! Use /predict_ewaste for predictions."}

@app.post("/predict_ewaste")
async def predict_ewaste(image_data: dict):
    """
    Receives a Base64 encoded image, runs YOLO inference, and returns detections.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="YOLO model is not loaded. Please check server logs for errors.")

    try:
        base64_string = image_data.get("image")
        if not base64_string:
            raise HTTPException(status_code=400, detail="No image data provided in the 'image' field.")

        # Decode Base64 string to bytes
        img_bytes = base64.b64decode(base64_string)
        # Open image using Pillow and ensure it's in RGB format
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        # Perform inference using the YOLO model
        # CUSTOM ADDITION 3:
        # Adjust 'conf' (confidence threshold) and 'iou' (NMS IoU threshold)
        # based on your model's performance and desired sensitivity.
        # 'save=False' prevents YOLO from saving prediction images to disk.
        results = model.predict(source=img, save=False, conf=0.4, iou=0.5)

        detections = []
        primary_ewaste_type = "no e-waste detected" # Default if nothing is found

        # Process results from YOLO
        for r in results:
            # r.boxes contains detected bounding boxes, confidence scores, and class IDs
            for box in r.boxes:
                x1, y1, x2, y2 = map(float, box.xyxy[0]) # Bounding box coordinates (top-left, bottom-right)
                confidence = float(box.conf[0])         # Confidence score of the detection
                class_id = int(box.cls[0])              # Class ID
                class_name = r.names[class_id]          # Class name (e.g., 'laptop', 'battery')

                detections.append({
                    "class_name": class_name,
                    "confidence": round(confidence, 4),
                    "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
                })

        # Determine the primary e-waste type for the UI
        # This simple logic picks the highest confidence detection that is in our info map.
        if detections:
            # Filter for detections that are actual e-waste types we have info for
            ewaste_detections_filtered = [d for d in detections if d['class_name'] in ewaste_info_map and d['class_name'] != 'no e-waste detected']

            if ewaste_detections_filtered:
                # Find the detection with the highest confidence among the filtered e-waste items
                highest_conf_detection = max(ewaste_detections_filtered, key=lambda x: x['confidence'])
                primary_ewaste_type = highest_conf_detection['class_name']
            # If no e-waste detections were found among the filtered ones, primary_ewaste_type remains 'no e-waste detected'

        # Return a JSON response with the prediction results
        return JSONResponse(content={
            "status": "success",
            "message": "E-waste prediction completed.",
            "primary_ewaste_type": primary_ewaste_type, # The single most relevant e-waste type
            "detections": detections # All raw detections (can be used for drawing bounding boxes on frontend)
        })

    except HTTPException as e:
        # Re-raise FastAPI HTTP exceptions (e.g., 400 Bad Request)
        raise e
    except Exception as e:
        # Catch any other unexpected errors during processing or inference
        print(f"Error during prediction: {e}")
        # Return a 500 Internal Server Error response
        raise HTTPException(status_code=500, detail=f"Internal server error during prediction: {e}")

@app.get("/hazards/{ewaste_type}")
async def get_hazards(ewaste_type: str):
    """
    Returns hazard information for a specific e-waste type from the predefined map.
    """
    # Convert input type to lowercase to match dictionary keys
    info = ewaste_info_map.get(ewaste_type.lower())
    if info:
        return JSONResponse(content={"ewaste_type": ewaste_type, "hazards": info['hazards']})
    # If the e-waste type is not found in the map, return a 404 Not Found error
    raise HTTPException(status_code=404, detail=f"Hazard information not found for e-waste type: {ewaste_type}.")