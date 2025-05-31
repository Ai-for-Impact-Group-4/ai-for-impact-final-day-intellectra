#AI for Impact Hackathon : Team Intellectra 
E-waste Identifier & Recycler : ECOCYCLE AI

#PROBLEM STATEMENT :
Electronic waste or e-waste is a rapidly growing global environmental and health concern. Improper disposal of e-waste leads to the release of toxic heavy metals (like lead, mercury, cadmium) and other hazardous chemicals into the soil, water, and air, posing severe risks to ecosystems and human health. Many individuals are unaware of what constitutes e-waste, its associated dangers, or proper recycling channels. This project aims to address this lack of awareness and accessibility to recycling solutions.

#OUR SOLUTION : 
Our "E-waste Identifier & Recycler" is an AI-powered web application designed to empower users to identify e-waste items, understand their potential hazards, and find nearby recycling options.

#THE APPLICATION HAS THE FOLLOWING FLOW :
~Image Upload: Users can upload an image of an item they suspect might be an e-waste.
~AI-Powered Identification: A custom-trained YOLO model(Yolov10n), deployed on a FastAPI backend, analyzes the uploaded image to determine if it is an e-waste and, if so, its specific type (e.g., laptop, smartphone, battery).
Right now, the YOLO model is trained on 11 classes, which are 'Computer', 'Dryer', 'Electronics', 'Headphone', 'Keyboard', 'Mobile', 'Modem', 'Mouse', 'PCB', 'Pendrive', 'Remote' and the map50-95 score is 
~Hazard Information: Based on the identified e-waste type, the application displays relevant information about the potential environmental and health hazards associated with that specific item.
~Recycling Suggestions: The application provides a list of mock nearby recycling/selling stores, guiding users towards proper disposal channels. (For the MVP, this uses mock data, but is designed for future integration with real-time location services).
This solution leverages cutting-edge AI for image recognition, combined with a user-friendly interface, to promote responsible e-waste management and contribute to environmental sustainability.

#API's USED:
~Custom YOLO Model (Backend):
Description: A custom-trained YOLOv10n object detection model, built using the ultralytics framework, is used for identifying and classifying various types of e-waste from images. The dataset used to train the images is "https://universe.roboflow.com/shubha-to6ii/e-waste-1sn3k".
Integration: The model is loaded and run on a FastAPI backend, which exposes a /predict_ewaste endpoint to the frontend.
~FastAPI (Backend Framework):
Description: A modern, fast (high-performance), web framework for building APIs with Python 3.7+. It's used to create the RESTful endpoint that serves the YOLO model's predictions.
Integration: Hosts the YOLO model and handles incoming image data, runs inference, and returns structured JSON responses.

#SETUP INSTRUCTIONS :
To set up and run this project locally, follow these steps:
1. Clone the repository in your terminal by the following command :
   git clone https://github.com/Ai-for-Impact-Group-4/ai-for-impact-final-day-intellectra.git
2. Go the directory created by the above command by typing :
   cd ai-for-impact-final-day-intellectra
3. Setup and run the backend by :
   cd backend
4. Install the necessary requirements by typing the following command:
   pip install -r requirements.txt
5. Run the server locally in your system as:
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
After running the uvicorn command, leave that terminal open, and open a NEW terminal window for the frontend:
6. In the NEW terminal, navigate back to the frontend of the project in following manner:
   cd D:\CODES\ai-for-impact-final-day-intellectra\frontend
7. Go the index.html and run it on live server.
The web app : ECOCYCLE AI is ready to use and promote sustainability 

#STRUCTURE OF THE REPO:
ai-for-impact-final-day-intellectra/
└── backend/
    ├── main.py
    ├── requirements.txt
    └── models/
        └── best(8).pt 
└── Frontend/
    ├── index.html
    ├── style.css
    └── style.js
└── README.md
└── .gitignore

#WHY DOES THESE FILES EXIST ?


#USAGE OF THE WEB APP:
1. Ensure both the backend server (on http://localhost:8000) and the frontend (your index.html file) are running.
2. Click "Browse File" to upload an image of a potential e-waste item.
3. Click "Analyze E-waste".
4. The application will send the image to backend, process it with the YOLO model, and display the identified e-waste type, its hazards, and mock recycling store suggestions.

#Screenshots

