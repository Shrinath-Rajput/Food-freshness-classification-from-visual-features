const express = require("express");
const multer = require("multer");
const axios = require("axios");
const mysql = require("mysql2/promise");
const fs = require("fs");
const FormData = require("form-data");

const app = express();
const PORT = process.env.PORT || 3000;

// ================= FLASK API =================
const FLASK_URL =
  process.env.FLASK_URL ||
  "https://your-flask-api.onrender.com"; // <-- CHANGE THIS

// ================= VIEW ENGINE =================
app.set("view engine", "ejs");

// ================= MIDDLEWARE =================
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static("public"));
app.use("/uploads", express.static("uploads"));

// ================= DB =================
let db;

(async () => {
  try {
    db = await mysql.createConnection({
      host: process.env.MYSQL_HOST,
      user: process.env.MYSQL_USER,
      password: process.env.MYSQL_PASSWORD,
      database: process.env.MYSQL_DATABASE,
      port: process.env.MYSQL_PORT
    });

    await db.query(`
      CREATE TABLE IF NOT EXISTS results (
        id INT AUTO_INCREMENT PRIMARY KEY,
        image VARCHAR(255),
        predicted_class VARCHAR(100),
        product_name VARCHAR(100),
        freshness VARCHAR(20),
        confidence FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    console.log("✅ MySQL Connected");

  } catch (err) {
    console.log("❌ DB ERROR:", err.message);
    db = null;
  }
})();

// ================= MULTER =================
const upload = multer({
  dest: "uploads/"
});

// ================= ROUTES =================

// HOME
app.get("/", (req, res) => {
  res.render("home");
});

// PREDICTION PAGE
app.get("/prediction", (req, res) => {
  res.render("prediction", {
    result: null,
    error: null
  });
});

// ================= PREDICT API =================
app.post("/predict", upload.single("image"), async (req, res) => {
  try {

    // FILE CHECK
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: "No image uploaded"
      });
    }

    const imagePath = req.file.path;

    console.log("📷 Uploaded:", imagePath);

    // CREATE FORM DATA
    const form = new FormData();

    form.append(
      "image",
      fs.createReadStream(imagePath)
    );

    console.log("🔥 Sending to Flask:", FLASK_URL);

    // ================= CALL FLASK =================
    const response = await axios.post(
      `${FLASK_URL}/api/predict`,
      form,
      {
        headers: form.getHeaders(),
        maxBodyLength: Infinity
      }
    );

    console.log("✅ Flask Response:", response.data);

    // RESPONSE CHECK
    if (!response.data.success) {
      throw new Error(
        response.data.error || "Prediction failed"
      );
    }

    const pred = response.data.prediction;

    const predicted_class = pred.class || "Unknown";
    const confidence = pred.confidence || 0;
    const freshness = pred.freshness || "Unknown";
    const product_name = pred.product_name || null;

    // ================= SAVE DB =================
    if (db) {

      await db.query(
        `
        INSERT INTO results
        (
          image,
          predicted_class,
          product_name,
          freshness,
          confidence
        )
        VALUES (?, ?, ?, ?, ?)
        `,
        [
          imagePath,
          predicted_class,
          product_name,
          freshness,
          confidence
        ]
      );

      console.log("✅ Saved to DB");

    } else {

      console.log("⚠️ DB not connected");

    }

    // ================= SUCCESS RESPONSE =================
    res.json({
      success: true,
      prediction: {
        class: predicted_class,
        confidence: confidence,
        freshness: freshness
      }
    });

  } catch (err) {

    console.error("❌ PREDICT ERROR:", err.message);

    res.status(500).json({
      success: false,
      error: err.message
    });

  }
});

// ================= DASHBOARD =================
app.get("/dashboard", async (req, res) => {

  try {

    if (!db) {
      throw new Error("Database not connected");
    }

    const [data] = await db.query(
      "SELECT * FROM results ORDER BY id DESC"
    );

    res.render("dashboard", {
      data,
      stats: {},
      productDist: [],
      classDist: [],
      error: null,
      page: 1,
      totalPages: 1
    });

  } catch (err) {

    res.render("dashboard", {
      data: [],
      stats: {},
      productDist: [],
      classDist: [],
      error: err.message,
      page: 1,
      totalPages: 1
    });

  }

});

// ================= DELETE =================
app.post("/delete/:id", async (req, res) => {

  try {

    if (db) {

      await db.query(
        "DELETE FROM results WHERE id=?",
        [req.params.id]
      );

    }

    res.redirect("/dashboard");

  } catch (err) {

    console.log(err.message);

    res.redirect("/dashboard");

  }

});

// ================= ANALYTICS =================
app.get("/analytics", async (req, res) => {

  try {

    if (!db) {
      throw new Error("Database not connected");
    }

    const [data] = await db.query(
      "SELECT * FROM results"
    );

    res.render("analytics", {
      data
    });

  } catch (err) {

    res.render("analytics", {
      data: []
    });

  }

});

// ================= SERVER =================
app.listen(PORT, () => {

  console.log(`
🚀 SERVER RUNNING
PORT: ${PORT}
FLASK: ${FLASK_URL}
  `);

});