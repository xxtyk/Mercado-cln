import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import router from "./routes/index.js";

const app = express();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// API
app.use("/api", router);

// 🔥 ADMIN FIX REAL
app.get("/admin", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../public/admin.html"));
});

// ARCHIVOS
app.use(express.static(path.join(__dirname, "../public")));

// FALLBACK
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

export default app;
