const express = require("express");
const router = express.Router();
const multer = require("multer");
const Product = require("../models/Product");

// Multer setup
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, "uploads/"),
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
});
const upload = multer({ storage });

// GET all products with optional category filter
router.get("/", async (req, res) => {
  try {
    const category = req.query.categoryId;
    const products = category
      ? await Product.find({ categoryId: category })
      : await Product.find();
    res.json(products);
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: err.message });
  }
});
router.get("/search", async (req, res) => {
  try {
    const text = req.query.q;
    if (!text) return res.json([]);

    const products = await Product.find({
      $or: [
        { "name.en": { $regex: text, $options: "i" } },
        { "name.ar": { $regex: text, $options: "i" } },
      ],
    });

    res.json(products);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET product by id
router.get("/:id", async (req, res) => {
  try {
    const product = await Product.findOne({ id: req.params.id });
    if (!product) return res.status(404).json({ message: "Product not found" });
    res.json(product);
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: err.message });
  }
});

// POST add product with image
router.post("/", upload.single("image"), async (req, res) => {
  try {
    const newProduct = new Product({
      ...req.body,
      image: req.file ? req.file.path : "",
    });
    await newProduct.save();
    res.status(201).json(newProduct);
  } catch (err) {
    console.log(err);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
