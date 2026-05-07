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
# Use __file__ instead of getcwd() for reliable path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "artifacts",
    "model.tflite"
)

print(f"🔥 BASE_DIR: {BASE_DIR}")
print(f"🔥 MODEL_PATH: {MODEL_PATH}")
print(f"🔥 Model exists: {os.path.exists(MODEL_PATH)}")

# ================= GLOBAL PREDICTOR (LAZY LOADED) =================
predictor = None

def get_predictor():
    """Lazy load predictor on first use"""
    global predictor
    if predictor is None:
        print("📦 Loading model predictor...")
        predictor = PredictPipeline(MODEL_PATH)
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
@app.route("/api/health")
def health():
    try:
        predictor = get_predictor()
        return jsonify({
            "status": "OK",
            "model_loaded": True,
            "model_path": MODEL_PATH
        })
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "model_loaded": False,
            "error": str(e),
            "model_path": MODEL_PATH
        }), 503


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

        # ================= LOAD PREDICTOR (LAZY LOAD) =================
        try:
            predictor = get_predictor()
        except Exception as e:
            print(f"❌ Failed to load predictor: {str(e)}")
            if os.path.exists(image_path):
                os.remove(image_path)
            return jsonify({
                "success": False,
                "error": f"Model loading failed: {str(e)}"
            }), 503

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