const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");
require("dotenv").config();

const Product = require("./models/Product");

const app = express();

// ===== Middleware =====
app.use(cors());
app.use(express.json());
app.use("/uploads", express.static("uploads"));

// ===== Routes القديمة =====
const productRoutes = require("./routes/products");
app.use("/", productRoutes);

// ===== Route الربط مع بايثون =====
app.post("/search", async (req, res) => {
  try {
    const { text } = req.body;

    if (!text) {
      return res.json({
        reply: "لم أفهم ما قلته، من فضلك أعد المحاولة",
      });
    }

    // البحث بالعربي أو الانجليزي
    const product = await Product.findOne({
      $or: [
        { "name.ar": { $regex: text, $options: "i" } },
        { "name.en": { $regex: text, $options: "i" } },
      ],
    });

    if (!product) {
      return res.json({
        reply: "المنتج غير متوفر حالياً",
      });
    }

    const reply =
      `المنتج ${product.name.ar} ` +
      `سعره ${product.price} جنيه ` +
      `وموجود في ${product.location.ar}`;

    res.json({
      reply,
      product,
    });
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: err.message });
  }
});

// ===== Mongo Connection =====
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => console.log("MongoDB connected"))
  .catch((err) => console.error("Mongo connection error:", err));

// ===== Run Server =====
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
