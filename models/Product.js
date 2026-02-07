const mongoose = require("mongoose");

const productSchema = new mongoose.Schema({
  id: { type: String, required: true },
  name: {
    en: String,
    ar: String,
  },
  categoryId: String,
  price: Number,
  image: String,
  location: {
    en: String,
    ar: String,
  },
  description: {
    en: String,
    ar: String,
  },
});

module.exports = mongoose.model("Product", productSchema);
