# main.py
import base64
import io
import os
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

# --- FastAPI App Initialization ---
app = FastAPI(
    title="E-waste YOLO Prediction API",
    description="API for E-waste detection using a custom YOLO model.",
    version="1.0.0"
)

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Model Loading ---
MODEL_PATH = r"models/best (8).pt"
model = None # Initialize model as None

@app.on_event("startup")
async def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: YOLO model not found at: {MODEL_PATH}. Please ensure your model is in the 'models' directory.")
        # Consider sys.exit(1) here in a production environment if the model is critical.
        return

    try:
        model = YOLO(MODEL_PATH)
        print(f"YOLO model loaded successfully from {MODEL_PATH}")
    except Exception as e:
        print(f"ERROR: Failed to load YOLO model from {MODEL_PATH}: {e}")
        model = None

# --- E-waste Info Map ---
ewaste_info_map = {
    "lcd monitor": { # Converted keys to lowercase for consistency
        "materials": "Lead, Mercury, Cadmium, Brominated Flame Retardants (BFRs)",
        "details": "LCD monitors contain mercury in their backlights, which is a neurotoxin. Lead in solder can harm the nervous system. Cadmium is a carcinogen and damages kidneys. BFRs are persistent organic pollutants.",
        "hazard_level": 4
    },
    "crt monitor": {
        "materials": "High levels of Lead, Barium, Mercury",
        "details": "CRT monitors are particularly hazardous due to high concentrations of lead in their glass (up to 5-8 pounds per unit), which is a severe neurotoxin. They also contain barium and mercury, posing significant environmental and health risks if improperly disposed of.",
        "hazard_level": 5
    },
    "printer": {
        "materials": "Lead, Mercury, Cadmium, Toner residue",
        "details": "Printers can contain lead in solder, mercury in some components, and cadmium. Toner cartridges contain fine plastic particles and heavy metals that can be harmful if inhaled or released into the environment.",
        "hazard_level": 3
    },
    "battery": {
        "materials": "Lithium, Lead, Cadmium, Mercury, Nickel (depending on type)",
        "details": "Batteries pose significant risks. Lithium-ion batteries can cause fires if damaged and contain cobalt and nickel. Lead-acid batteries contain corrosive sulfuric acid and lead, a neurotoxin. Cadmium and mercury in other battery types are highly toxic and bioaccumulate.",
        "hazard_level": 5
    },
    "cable": {
        "materials": "PVC (Polyvinyl Chloride), Lead, Cadmium, Brominated Flame Retardants",
        "details": "Cables often contain PVC, which releases dioxins when burned. Lead and cadmium are sometimes used in insulation and solder, posing neurotoxic and carcinogenic risks. BFRs are used as flame retardants and are persistent environmental pollutants.",
        "hazard_level": 2
    },
    "no e-waste detected": { # Consistent key
        "materials": "N/A (Not E-Waste)",
        "details": "This item was not identified as e-waste. While not containing specific e-waste hazards, please ensure proper disposal according to local waste management guidelines to prevent general pollution.",
        "hazard_level": 1
    },
    "computer": {
        "materials": "Lead, Mercury, Cadmium, Chromium, Brominated Flame Retardants (BFRs), PVC",
        "details": "Computers are complex and contain numerous hazardous materials. Lead in solder, mercury in LCD backlights, and cadmium are highly toxic. Chromium can be carcinogenic. BFRs are persistent environmental pollutants. PVC releases dioxins upon incineration.",
        "hazard_level": 5
    },
    "dryer": {
        "materials": "Lead (solder), some PCBs, occasional Mercury switches, various plastics",
        "details": "While less electronic than computers, dryers can contain lead in solder, small printed circuit boards (PCBs) with heavy metals, and older models might have mercury switches. Plastics and other metals should also be recycled responsibly.",
        "hazard_level": 3
    },
    "electronics": {
        "materials": "Lead, Mercury, Cadmium, Brominated Flame Retardants (BFRs), PVC, Lithium",
        "details": "This general category of electronics can contain a wide array of hazardous substances including heavy metals like lead, mercury, and cadmium which are toxic to human health and the environment. Brominated Flame Retardants (BFRs) are persistent pollutants, and lithium from batteries poses fire risks and environmental contamination.",
        "hazard_level": 4
    },
    "headphone": {
        "materials": "Plastics, Lead (solder), small PCBs, trace rare earth metals",
        "details": "Headphones primarily consist of plastics and metals. Small amounts of lead may be present in solder on internal PCBs. They also contain tiny amounts of rare earth metals, which are valuable but mining can be environmentally intensive.",
        "hazard_level": 2
    },
    "keyboard": {
        "materials": "Plastics, Lead (solder), small PCBs, some metals",
        "details": "Keyboards are mainly plastics, but also contain small circuit boards with lead solder and other metals. While the individual hazard level is lower, the sheer volume of discarded keyboards contributes to e-waste accumulation.",
        "hazard_level": 2
    },
    "mobile": {
        "materials": "Lithium-ion battery, Lead, Mercury, Cadmium, Arsenic, BFRs, rare earth metals",
        "details": "Mobile phones are highly complex and contain numerous toxic elements. Lithium-ion batteries pose fire hazards and contain cobalt and nickel. Lead, mercury, cadmium, and arsenic are severe neurotoxins and carcinogens. BFRs and valuable rare earth metals are also present.",
        "hazard_level": 5
    },
    "modem": {
        "materials": "Lead (solder), Brominated Flame Retardants (BFRs), PVC, various plastics",
        "details": "Modems contain PCBs with lead solder. Brominated Flame Retardants (BFRs) are often used in their plastic casings and internal components. PVC plastic can also be present, which creates dioxins if incinerated.",
        "hazard_level": 3
    },
    "mouse": {
        "materials": "Plastics, Lead (solder), small PCBs",
        "details": "Computer mice are mostly plastics, but like keyboards, they contain small printed circuit boards (PCBs) that utilize lead solder. Proper recycling prevents these metals from leaching into the environment.",
        "hazard_level": 2
    },
    "pcb": { # Printed Circuit Board
        "materials": "Lead, Mercury, Cadmium, Brominated Flame Retardants (BFRs), Chromium, Arsenic, Beryllium",
        "details": "Printed Circuit Boards are the core of most electronics and are highly hazardous. They contain a cocktail of heavy metals like lead, mercury, cadmium, and chromium, all of which are toxic. Beryllium and arsenic are also present, along with BFRs, making PCBs a major environmental concern.",
        "hazard_level": 5
    },
    "pendrive": {
        "materials": "Small PCB, flash memory (silicon, trace metals), plastics",
        "details": "Pendrives contain a small printed circuit board with lead solder and flash memory chips with various trace metals. While small, the cumulative effect of improper disposal of many such devices contributes to environmental pollution.",
        "hazard_level": 2
    },
    "remote": {
        "materials": "Plastics, Lead (solder), small PCBs, batteries (often alkaline)",
        "details": "Remote controls are largely plastic with a small internal PCB. Lead is present in solder. While they often use less hazardous alkaline batteries, any battery should be disposed of properly.",
        "hazard_level": 1
    },
    "other_ewaste": {
        "materials": "Various, depends on specific components", # Added materials for consistency
        "details": "Generic e-waste can contain a mix of plastics, metals, and various hazardous substances depending on the specific components. Proper disposal is crucial to prevent environmental contamination.",
        "hazard_level": 3 # Assigned a default hazard level
    }
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

        img_bytes = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

        results = model.predict(source=img, save=False, conf=0.4, iou=0.5)

        detections = []
        primary_ewaste_type = "no e-waste detected" # Default if nothing is found
        highest_confidence = 0.0

        for r in results:
            for box in r.boxes:
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = r.names[class_id].lower() # Convert class name to lowercase

                x1, y1, x2, y2 = map(float, box.xyxy[0])

                detections.append({
                    "class_name": class_name,
                    "confidence": round(confidence, 4),
                    "bbox": [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]
                })

                # Determine the primary e-waste type based on highest confidence
                if class_name in ewaste_info_map and confidence > highest_confidence:
                    primary_ewaste_type = class_name
                    highest_confidence = confidence

        # If after checking all detections, no e-waste was identified from the map,
        # ensure primary_ewaste_type reflects "no e-waste detected" as per its initial value.
        # This is already handled by the initial assignment and conditional updates.

        # Retrieve information for the primary e-waste type
        primary_ewaste_info = ewaste_info_map.get(primary_ewaste_type, ewaste_info_map["no e-waste detected"])

        return JSONResponse(content={
            "status": "success",
            "message": "E-waste prediction completed.",
            "primary_ewaste_type": primary_ewaste_type,
            "primary_ewaste_info": primary_ewaste_info, # Added detailed info for the primary type
            "detections": detections
        })

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during prediction: {e}")

@app.get("/hazards/{ewaste_type}")
async def get_hazards(ewaste_type: str):
    """
    Returns hazard information for a specific e-waste type from the predefined map.
    """
    info = ewaste_info_map.get(ewaste_type.lower())
    if info:
        # Return all details from the ewaste_info_map, not just 'hazards'
        return JSONResponse(content={"ewaste_type": ewaste_type, **info})
    raise HTTPException(status_code=404, detail=f"Hazard information not found for e-waste type: {ewaste_type}.")