const express = require("express");
const multer = require("multer");
const axios = require("axios");
const mysql = require("mysql2/promise");
const fs = require("fs");
const path = require("path");
const FormData = require("form-data");

const app = express();
const PORT = process.env.PORT || 3000;

// ⚠️ Flask API (Railway env मधून)
const FLASK_URL = process.env.FLASK_URL;

app.set("view engine", "ejs");
app.use(express.urlencoded({ extended: true }));
app.use(express.static("public"));
app.use("/uploads", express.static("uploads"));

// ================= DB =================
let db;

(async () => {
  try {
    db = await mysql.createConnection({
      host: process.env.MYSQLHOST,
      user: process.env.MYSQLUSER,
      password: process.env.MYSQLPASSWORD,
      database: process.env.MYSQLDATABASE,
      port: process.env.MYSQLPORT
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

    console.log("✅ DB Connected");
  } catch (err) {
    console.log("❌ DB ERROR:", err.message);
  }
})();

// ================= MULTER =================
const upload = multer({ dest: "uploads/" });

// ================= ROUTES =================

app.get("/", (req, res) => {
  res.render("home");
});

app.get("/prediction", (req, res) => {
  res.render("prediction", { result: null, error: null });
});

// ================= PREDICT =================
app.post("/predict", upload.single("image"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: "No file uploaded"
      });
    }

    const imagePath = req.file.path;

    const form = new FormData();
    form.append("image", fs.createReadStream(imagePath));

    // 🔥 CALL FLASK
    const response = await axios.post(`${FLASK_URL}/api/predict`, form, {
      headers: form.getHeaders()
    });

    console.log("🔥 Flask response:", response.data);

    if (!response.data.success) {
      throw new Error(response.data.error || "Flask prediction failed");
    }

    const pred = response.data.prediction;

    const predicted_class = pred.class;
    const confidence = pred.confidence;
    const freshness = pred.freshness;
    const product_name = null;

    // ================= SAVE =================
    await db.query(
      `INSERT INTO results 
      (image, predicted_class, product_name, freshness, confidence)
      VALUES (?, ?, ?, ?, ?)`,
      [imagePath, predicted_class, product_name, freshness, confidence]
    );

    console.log("✅ Saved to DB");

    res.json({
      success: true,
      prediction: {
        class: predicted_class,
        confidence: confidence,
        freshness: freshness
      }
    });

  } catch (err) {
    console.error("❌ ERROR:", err.message);

    res.status(500).json({
      success: false,
      error: err.message
    });
  }
});

// ================= DASHBOARD =================
app.get("/dashboard", async (req, res) => {
  try {
    const [data] = await db.query("SELECT * FROM results ORDER BY id DESC");

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
  await db.query("DELETE FROM results WHERE id=?", [req.params.id]);
  res.redirect("/dashboard");
});

// ================= ANALYTICS =================
app.get("/analytics", async (req, res) => {
  try {
    const [data] = await db.query("SELECT * FROM results");
    res.render("analytics", { data });
  } catch (err) {
    res.render("analytics", { data: [] });
  }
});

// ================= START =================
app.listen(PORT, () => {
  console.log(`🚀 Server running`);
});