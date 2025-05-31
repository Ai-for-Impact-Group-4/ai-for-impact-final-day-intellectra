E-waste Identifier & Recycler (AI for Impact Hackathon)

💡 Problem Statement
Electronic waste (e-waste) is a rapidly growing global environmental and health concern. Improper disposal of e-waste leads to the release of toxic heavy metals (like lead, mercury, cadmium) and other hazardous chemicals into the soil, water, and air, posing severe risks to ecosystems and human health. Many individuals are unaware of what constitutes e-waste, its associated dangers, or proper recycling channels. This project aims to address this lack of awareness and accessibility to recycling solutions.

🚀 Solution Overview
Our "E-waste Identifier & Recycler" is an AI-powered web application designed to empower users to identify e-waste items, understand their potential hazards, and find nearby recycling options.

The application works as follows:

Image Upload: Users can upload an image of an item they suspect might be e-waste.

AI-Powered Identification: A custom-trained YOLO model(Yolov10n), deployed on a FastAPI backend, analyzes the uploaded image to determine if it is e-waste and, if so, its specific type (e.g., laptop, smartphone, battery).

Hazard Information: Based on the identified e-waste type, the application displays relevant information about the potential environmental and health hazards associated with that specific item.

Recycling Suggestions: The application provides a list of mock nearby recycling/selling stores, guiding users towards proper disposal channels. (For the MVP, this uses mock data, but is designed for future integration with real-time location services).

This solution leverages cutting-edge AI for image recognition, combined with a user-friendly interface, to promote responsible e-waste management and contribute to environmental sustainability.

⚙️ API(s) Used
Custom YOLO Model (Backend):

Description: A custom-trained YOLOv10 object detection model, built using the ultralytics framework, is used for identifying and classifying various types of e-waste from images.

Integration: The model is loaded and run on a FastAPI backend, which exposes a /predict_ewaste endpoint to the frontend.


FastAPI (Backend Framework):

Description: A modern, fast (high-performance), web framework for building APIs with Python 3.7+. It's used to create the RESTful endpoint that serves the YOLO model's predictions.

Integration: Hosts the YOLO model and handles incoming image data, runs inference, and returns structured JSON responses.

🛠️ Setup Instructions
To set up and run this project locally, follow these steps:

Prerequisites
Python 3.8+

pip (Python package installer)

git

Node.js (for npm if you use Live Server extension in VS Code)

Your trained YOLO model file (e.g., yolov8s_ewaste.pt)

1. Clone the Repository
First, clone the GitHub Classroom repository to your local machine:

git clone https://github.com/Ai-for-Impact-Group-4/ai-for-impact-final-day-intellectra
cd ai-for-impact-final-day-intellectra

2. Backend Setup
Navigate into the backend directory, set up the Python environment, and place your YOLO model.

cd backend

a. Place Your YOLO Model
Create a models directory inside the backend folder and place your trained YOLO model file (e.g., yolov8s_ewaste.pt, best.pt) inside it.

ai-for-impact-final-day-intellectra/
└── backend/
    ├── main.py
    ├── requirements.txt
    └── models/
        └── yolov8s_ewaste.pt  <-- YOUR TRAINED YOLO MODEL FILE GOES HERE

b. Install Python Dependencies
Install the required Python libraries using pip:

pip install -r requirements.txt

c. Run the Backend Server
Start the FastAPI server. This server will host your YOLO model and provide the prediction API.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Keep this terminal window open; the server needs to be running for the frontend to work.

3. Frontend Setup
The frontend is a simple HTML file. You can open it directly in your browser or use a local server for convenience.

cd ../frontend # Go back to the root, then into frontend

a. Open index.html in a Browser
You can simply open the index.html file in your web browser (e.g., by double-clicking it in your file explorer).

b. (Recommended) Use VS Code Live Server Extension
For easier development and to avoid CORS issues with file:// URLs, it's recommended to use the "Live Server" extension in VS Code:

If you don't have it, install the "Live Server" extension from the VS Code Extensions marketplace.

In VS Code, right-click on index.html in the frontend folder.

Select "Open with Live Server". This will open the frontend in your browser, typically at http://127.0.0.1:5500/frontend/index.html.

4. Usage
Ensure both the backend server (on http://localhost:8000) and the frontend (your index.html file) are running.

In the frontend, click "Choose File" to upload an image of a potential e-waste item.

Click "Analyze E-waste".

The application will send the image to your backend, process it with the YOLO model, and display the identified e-waste type, its hazards, and mock recycling store suggestions.

📸 Screenshots
(You will add screenshots of your running application here. For example:)

Main Upload Interface:


Analysis Results:


Recycling Store Suggestions:
