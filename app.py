from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.Pipeline.predict_pipeline import PredictPipeline

# ================= APP =================
app = Flask(__name__)

# ================= FOLDERS =================
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= MODEL PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "artifacts",
    "model.tflite"
)

print("🚀 Flask Starting...")
print("📂 BASE_DIR:", BASE_DIR)
print("📦 MODEL_PATH:", MODEL_PATH)
print("✅ MODEL EXISTS:", os.path.exists(MODEL_PATH))

# ================= GLOBAL PREDICTOR =================
predictor = None


def get_predictor():

    global predictor

    if predictor is None:

        print("📦 Loading Model...")

        predictor = PredictPipeline(MODEL_PATH)

        print("✅ Model Loaded")

    return predictor


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
@app.route("/health")
def health():

    try:

        predictor = get_predictor()

        return jsonify({
            "success": True,
            "model_loaded": True,
            "model_path": MODEL_PATH
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():

    try:

        # ================= FILE CHECK =================
        if "image" not in request.files:

            return jsonify({
                "success": False,
                "error": "No image uploaded"
            }), 400

        file = request.files["image"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "error": "Empty filename"
            }), 400

        # ================= SAVE FILE =================
        filename = secure_filename(file.filename)

        image_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(image_path)

        print("📷 IMAGE SAVED:", image_path)

        # ================= LOAD MODEL =================
        predictor = get_predictor()

        # ================= PREDICT =================
        result = predictor.predict(
            image_path,
            CLASS_INDICES
        )

        print("🔥 RESULT:", result)

        # ================= DELETE IMAGE =================
        if os.path.exists(image_path):

            os.remove(image_path)

        # ================= VALIDATE =================
        if not result:

            return jsonify({
                "success": False,
                "error": "Prediction failed"
            }), 500

        predicted_class = result.get(
            "class",
            "Unknown"
        )

        confidence = float(
            result.get(
                "confidence",
                0
            )
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
        }), 500


# ================= START =================
if __name__ == "__main__":

    PORT = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )