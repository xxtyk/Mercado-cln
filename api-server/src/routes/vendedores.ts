import { Router } from "express";
import pool from "../db.js";

const router = Router();
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function autenticado(req: any, res: any): boolean {
  const auth = req.headers.authorization ?? "";
  if (auth !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

// VER VENDEDORES
router.get("/vendedores", async (_req, res) => {
  try {
    const result = await pool.query(
      "SELECT id, nombre FROM vendedores ORDER BY nombre ASC"
    );
    return res.json(result.rows);
  } catch (error) {
    console.error("ERROR GET /vendedores:", error);
    return res.status(500).json({ ok: false, error: "Error obteniendo vendedores" });
  }
});

// CREAR VENDEDOR
router.post("/vendedores", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const nombre = String(req.body?.nombre || "").trim();

    if (!nombre) {
      return res.status(400).json({ ok: false, error: "Falta nombre" });
    }

    const repetido = await pool.query(
      "SELECT 1 FROM vendedores WHERE LOWER(nombre) = LOWER($1) LIMIT 1",
      [nombre]
    );

    if (repetido.rows.length > 0) {
      return res.status(400).json({ ok: false, error: "Ese vendedor ya existe" });
    }

    const result = await pool.query(
      "INSERT INTO vendedores (nombre) VALUES ($1) RETURNING id, nombre",
      [nombre]
    );

    return res.json({ ok: true, vendedor: result.rows[0] });
  } catch (error) {
    console.error("ERROR POST /vendedores:", error);
    return res.status(500).json({ ok: false, error: "Error guardando vendedor" });
  }
});

// EDITAR VENDEDOR
router.put("/vendedores/:id", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const id = Number(req.params.id);
    const nombre = String(req.body?.nombre || "").trim();

    if (!nombre) {
      return res.status(400).json({ ok: false, error: "Falta nombre" });
    }

    const existe = await pool.query(
      "SELECT 1 FROM vendedores WHERE id = $1 LIMIT 1",
      [id]
    );

    if (existe.rows.length === 0) {
      return res.status(404).json({ ok: false, error: "Vendedor no encontrado" });
    }

    const repetido = await pool.query(
      "SELECT 1 FROM vendedores WHERE LOWER(nombre) = LOWER($1) AND id <> $2 LIMIT 1",
      [nombre, id]
    );

    if (repetido.rows.length > 0) {
      return res.status(400).json({ ok: false, error: "Ese vendedor ya existe" });
    }

    const result = await pool.query(
      "UPDATE vendedores SET nombre = $1 WHERE id = $2 RETURNING id, nombre",
      [nombre, id]
    );

    return res.json({ ok: true, vendedor: result.rows[0] });
  } catch (error) {
    console.error("ERROR PUT /vendedores/:id:", error);
    return res.status(500).json({ ok: false, error: "Error actualizando vendedor" });
  }
});

// ELIMINAR VENDEDOR
router.delete("/vendedores/:id", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const id = Number(req.params.id);

    const result = await pool.query(
      "DELETE FROM vendedores WHERE id = $1",
      [id]
    );

    if ((result.rowCount ?? 0) === 0) {
      return res.status(404).json({ ok: false, error: "Vendedor no encontrado" });
    }

    return res.json({ ok: true });
  } catch (error) {
    console.error("ERROR DELETE /vendedores/:id:", error);
    return res.status(500).json({ ok: false, error: "Error eliminando vendedor" });
  }
});

export default router;
