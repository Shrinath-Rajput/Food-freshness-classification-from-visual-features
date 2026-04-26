import tensorflow as tf

# 🔹 Load your trained model
model = tf.keras.models.load_model("artifacts/model.h5")

print("✅ Model loaded")

# 🔹 Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

print("✅ Converted to TFLite")

# 🔹 Save file
with open("artifacts/model.tflite", "wb") as f:
    f.write(tflite_model)

print("🎉 Saved as artifacts/model.tflite")