from flask import Flask, request, render_template, jsonify
import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Secure API Key (Don't expose in code)
API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

if not API_KEY:
    raise ValueError("❌ Error: Gemini API Key is missing. Set GEMINI_API_KEY in your environment variables.")

#@app.route("/")
#def index():
 #   return render_template("index.html")

@app.route("/")
def index():
    print("Rendering index.html")  # Debugging statement
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    image = request.files["image"]
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    # Call Gemini API for calorie estimation
    calories = detect_calories(image_path)

    return jsonify({"calories": calories})

import base64
import requests
import json

def detect_calories(image_path):
    """Send the food image to Gemini API and get calorie estimate."""
    
    # Convert image to Base64
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    headers = {
        "Content-Type": "application/json",
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": "Estimate the number of calories in this food image."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
                ]
            }
        ]
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        try:
            # Extract the AI response
            calories_info = data["candidates"][0]["content"]["parts"][0]["text"]
            return calories_info
        except (KeyError, IndexError):
            return "Error: Unexpected API response format"
    else:
        return f"Error: Unable to process image (Status: {response.status_code}, Message: {response.text})"


if __name__ == "__main__":
    app.run(debug=True)
