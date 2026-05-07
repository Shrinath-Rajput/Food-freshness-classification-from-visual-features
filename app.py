from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.Pipeline.predict_pipeline import PredictPipeline

# ================= APP INIT =================
app = Flask(__name__)

# ================= FOLDERS =================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= MODEL PATH =================
BASE_DIR = os.getcwd()

MODEL_PATH = os.path.join(
    BASE_DIR,
    "artifacts",
    "model.tflite"
)

print("🔥 MODEL PATH:", MODEL_PATH)

# ================= LOAD MODEL =================
predictor = PredictPipeline(MODEL_PATH)

# ================= CLASSES =================
CLASS_INDICES = {
    "freshapple": 0,
    "rottenapple": 1
}

# ================= HOME =================
@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "Food Freshness API Running 🚀"
    })


# ================= HEALTH =================
@app.route("/api/health")
def health():

    return jsonify({
        "status": "OK"
    })


# ================= PREDICT =================
@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        # ================= CHECK FILE =================
        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No file uploaded"
            })

        file = request.files["image"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "error": "Empty filename"
            })

        # ================= SAVE IMAGE =================
        filename = secure_filename(file.filename)

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(image_path)

        print("🔥 IMAGE SAVED:", image_path)

        # ================= PREDICT =================
        result = predictor.predict(
            image_path,
            CLASS_INDICES
        )

        print("🔥 RESULT:", result)

        # ================= DELETE TEMP IMAGE =================
        if os.path.exists(image_path):

            os.remove(image_path)

        # ================= VALIDATION =================
        if not result:

            return jsonify({
                "success": False,
                "error": "Prediction failed"
            })

        if "class" not in result:

            return jsonify({
                "success": False,
                "error": "Class not found"
            })

        predicted_class = result["class"]

        confidence = float(
            result["confidence"]
        )

        # ================= FRESHNESS =================
        freshness = "Fresh"

        if "rotten" in predicted_class.lower():

            freshness = "Rotten"

        # ================= RESPONSE =================
        return jsonify({
            "success": True,
            "prediction": {
                "class": predicted_class,
                "freshness": freshness,
                "confidence": confidence
            }
        })

    except Exception as e:

        print("❌ ERROR:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        })


# ================= START =================
if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 10000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )