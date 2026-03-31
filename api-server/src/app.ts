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

// 🔥 1. ADMIN PRIMERO (ANTES DE TODO)
app.get("/admin", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../public/admin.html"));
});

// 🔥 2. API
app.use("/api", router);

// 🔥 3. ARCHIVOS PUBLICOS
app.use(express.static(path.resolve(__dirname, "../public")));

// 🔥 4. FALLBACK (LO ÚLTIMO SIEMPRE)
app.get("*", (req, res) => {
  res.sendFile(path.resolve(__dirname, "../public/index.html"));
});

export default app;
