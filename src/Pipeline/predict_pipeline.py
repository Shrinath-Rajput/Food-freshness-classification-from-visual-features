import os
import numpy as np
import tflite_runtime.interpreter as tflite
from tensorflow.keras.preprocessing.image import load_img, img_to_array


class PredictPipeline:

    def __init__(self, model_path):

        if not os.path.exists(model_path):
            raise Exception(f"Model not found: {model_path}")

        # ================= LOAD MODEL =================
        self.interpreter = tflite.Interpreter(
            model_path=model_path
        )

        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        print("✅ TFLite model loaded")


    def predict(self, image_path, class_indices):

        try:

            # ================= LOAD IMAGE =================
            img = load_img(
                image_path,
                target_size=(224, 224)
            )

            img = img_to_array(img)

            img = img.astype(np.float32) / 255.0

            img = np.expand_dims(img, axis=0)

            # ================= INPUT =================
            self.interpreter.set_tensor(
                self.input_details[0]['index'],
                img
            )

            # ================= RUN MODEL =================
            self.interpreter.invoke()

            # ================= OUTPUT =================
            preds = self.interpreter.get_tensor(
                self.output_details[0]['index']
            )[0]

            print("🔥 RAW PREDICTION:", preds)

            idx = int(np.argmax(preds))

            confidence = float(preds[idx])

            class_names = list(class_indices.keys())

            predicted_class = class_names[idx]

            return {
                "class": predicted_class,
                "confidence": confidence
            }

        except Exception as e:

            print("❌ PREDICT ERROR:", str(e))

            return {
                "class": "unknown",
                "confidence": 0
            }