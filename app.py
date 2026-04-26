from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
from src.Pipeline.predict_pipeline import PredictPipeline

# ✅ APP INIT
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ LOAD TFLITE MODEL (FIXED)
predictor = PredictPipeline("artifacts/model.tflite")

CLASS_INDICES = {
    "freshapple": 0,
    "rottenapple": 1
}

# ================= HEALTH =================
@app.route("/api/health")
def health():
    return {"status": "OK"}


# ================= PREDICT =================
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if "image" not in request.files:
            return {"success": False, "error": "No file uploaded"}

        file = request.files["image"]
        filename = secure_filename(file.filename)

        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        # 🔥 PREDICT
        result = predictor.predict(path, CLASS_INDICES)

        # 🧹 delete temp file
        if os.path.exists(path):
            os.remove(path)

        # safety check
        if not result or "class" not in result:
            return {"success": False, "error": "Prediction failed"}

        freshness = "Fresh" if "fresh" in result["class"] else "Rotten"

        return jsonify({
            "success": True,
            "prediction": {
                "class": result["class"],
                "freshness": freshness,
                "confidence": float(result["confidence"])
            }
        })

    except Exception as e:
        print("❌ ERROR:", e)
        return {"success": False, "error": str(e)}


# ================= START =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # ✅ Railway fix
    app.run(host="0.0.0.0", port=port)