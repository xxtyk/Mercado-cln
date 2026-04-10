import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import router from "./routes/index.js";

const app = express();

// rutas de sistema
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PUBLIC_DIR = path.resolve(__dirname, "../public");

// middlewares
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 🔥 SERVIR IMÁGENES SUBIDAS
app.use("/api/uploads", express.static(path.join(process.cwd(), "uploads")));

// 🔥 ADMIN
app.get("/admin", (_req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, "admin.html"));
});

app.get("/admin.html", (_req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, "admin.html"));
});

// 🔥 API
app.use("/api", router);

// 🔥 ARCHIVOS PÚBLICOS (CATÁLOGO)
app.use(express.static(PUBLIC_DIR));

// 🔥 FALLBACK (para que siempre cargue index.html)
app.get("*", (_req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, "index.html"));
});

export default app;
