import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import router from "./routes/index.js";

const app = express();

// 👉 FIX rutas (IMPORTANTE)
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 👉 API
app.use("/api", router);

// 👉 ADMIN (ARREGLADO)
app.get("/admin", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/admin.html"));
});

// 👉 ARCHIVOS PUBLICOS
app.use(express.static(path.join(__dirname, "../public")));

// 👉 TODO LO DEMÁS
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "../public/index.html"));
});

export default app;
