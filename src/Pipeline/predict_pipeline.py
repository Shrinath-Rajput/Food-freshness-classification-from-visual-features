import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array

class PredictPipeline:
    def __init__(self, model_path="artifacts/model.tflite"):
        if not os.path.exists(model_path):
            raise Exception("Model not found")

        # 🔥 Load TFLite model
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, image_path, class_indices):
        try:
            # ✅ Image preprocess
            img = load_img(image_path, target_size=(224, 224))
            img = img_to_array(img) / 255.0
            img = np.expand_dims(img, axis=0).astype(np.float32)

            # 🔥 Set input
            self.interpreter.set_tensor(self.input_details[0]['index'], img)

            # 🔥 Run inference
            self.interpreter.invoke()

            # 🔥 Get output
            preds = self.interpreter.get_tensor(self.output_details[0]['index'])[0]

            print("🔥 RAW:", preds)

            idx = int(np.argmax(preds))
            confidence = float(preds[idx])

            # ✅ SAFE mapping
            class_names = list(class_indices.keys())

            if len(class_names) == 0:
                return {"class": "unknown", "confidence": 0}

            if idx >= len(class_names):
                idx = 0

            class_name = class_names[idx]

            return {
                "class": class_name,
                "confidence": confidence
            }

        except Exception as e:
            print("❌ ERROR IN PREDICT:", e)
            return {"class": "unknown", "confidence": 0}