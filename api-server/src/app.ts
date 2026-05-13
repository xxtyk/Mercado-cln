import express from "express";
import cors from "cors";
import path from "path";
import { fileURLToPath } from "url";
import router from "./routes/index.js";
import vendedores from "./routes/vendedores.js";
import pool from "./db.js";

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

// 👥 GUARDAR VISITA
app.post("/api/visita", async (_req, res) => {
  try {

    await pool.query(`
      CREATE TABLE IF NOT EXISTS visitas (
        id SERIAL PRIMARY KEY,
        creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      )
    `);

    await pool.query(`
      INSERT INTO visitas DEFAULT VALUES
    `);

    res.json({ ok: true });

  } catch (err) {

    console.log(err);

    res.status(500).json({
      ok: false
    });

  }
});

// 👥 VISITAS DE HOY
app.get("/api/visitas-hoy", async (_req, res) => {

  try {

    const result = await pool.query(`
      SELECT COUNT(*) AS total
      FROM visitas
      WHERE DATE(creado) = CURRENT_DATE
    `);

    res.json({
      total: result.rows[0].total
    });

  } catch (err) {

    console.log(err);

    res.json({
      total: 0
    });

  }

});

// 🔥 API
app.use("/api", router);
app.use("/api", vendedores);

// 🔥 ARCHIVOS PÚBLICOS (CATÁLOGO)
app.use(express.static(PUBLIC_DIR));

// 🔥 FALLBACK (para que siempre cargue index.html)
app.get("*", (_req, res) => {
  res.sendFile(path.join(PUBLIC_DIR, "index.html"));
});

export default app;
