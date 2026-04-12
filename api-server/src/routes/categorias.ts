import { Router } from "express";
import pool from "../db.js";

const router = Router();
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function auth(req: any, res: any): boolean {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

function generarSlug(nombre: string) {
  return String(nombre || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "") || "otro";
}

function tomarImagen(body: any, actual = ""): string {
  if (body?.imagen !== undefined) return String(body.imagen || "").trim();
  if (body?.foto !== undefined) return String(body.foto || "").trim();
  if (body?.image !== undefined) return String(body.image || "").trim();
  if (body?.imageUrl !== undefined) return String(body.imageUrl || "").trim();
  return String(actual || "").trim();
}

// GET
router.get("/categorias", async (_req, res) => {
  try {
    const result = await pool.query(
      "SELECT id, slug, nombre, emoji, imagen FROM categorias ORDER BY nombre ASC"
    );
    return res.json(result.rows);
  } catch (error) {
    console.error("ERROR GET /categorias:", error);
    return res.status(500).json({ ok: false, error: "Error obteniendo categorías" });
  }
});

// POST
router.post("/categorias", async (req: any, res) => {
  if (!auth(req, res)) return;

  try {
    const nombre = String(req.body?.nombre || "").trim();
    const emoji = String(req.body?.emoji || "🛍️").trim() || "🛍️";
    const imagen = tomarImagen(req.body, "");

    if (!nombre) {
      return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
    }

    let slug = generarSlug(nombre);

    const repetida = await pool.query(
      "SELECT 1 FROM categorias WHERE slug = $1 LIMIT 1",
      [slug]
    );

    if (repetida.rows.length > 0) {
      slug = `${slug}_${Date.now()}`;
    }

    const id = Date.now().toString();

    const result = await pool.query(
      `
      INSERT INTO categorias (id, slug, nombre, emoji, imagen)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING id, slug, nombre, emoji, imagen
      `,
      [id, slug, nombre, emoji, imagen]
    );

    return res.json({ ok: true, categoria: result.rows[0] });
  } catch (error) {
    console.error("ERROR POST /categorias:", error);
    return res.status(500).json({ ok: false, error: "Error creando categoría" });
  }
});

// PUT
router.put("/categorias/:id", async (req: any, res) => {
  if (!auth(req, res)) return;

  try {
    const actualResult = await pool.query(
      "SELECT * FROM categorias WHERE id = $1 LIMIT 1",
      [req.params.id]
    );

    if (actualResult.rows.length === 0) {
      return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
    }

    const actual = actualResult.rows[0];

    const nombre = String(req.body?.nombre || actual.nombre || "").trim();
    const emoji = String(req.body?.emoji ?? actual.emoji ?? "🛍️").trim() || "🛍️";
    const imagen = tomarImagen(req.body, actual.imagen || "");

    if (!nombre) {
      return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
    }

    let slug = generarSlug(nombre);

    const repetida = await pool.query(
      "SELECT 1 FROM categorias WHERE slug = $1 AND id <> $2 LIMIT 1",
      [slug, req.params.id]
    );

    if (repetida.rows.length > 0) {
      slug = `${slug}_${Date.now()}`;
    }

    const result = await pool.query(
      `
      UPDATE categorias
      SET nombre = $1, slug = $2, emoji = $3, imagen = $4
      WHERE id = $5
      RETURNING id, slug, nombre, emoji, imagen
      `,
      [nombre, slug, emoji, imagen, req.params.id]
    );

    return res.json({ ok: true, categoria: result.rows[0] });
  } catch (error) {
    console.error("ERROR PUT /categorias/:id:", error);
    return res.status(500).json({ ok: false, error: "Error actualizando categoría" });
  }
});

// DELETE
router.delete("/categorias/:id", async (req: any, res) => {
  if (!auth(req, res)) return;

  try {
    const result = await pool.query(
      "DELETE FROM categorias WHERE id = $1",
      [req.params.id]
    );

    if (result.rowCount === 0) {
      return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
    }

    return res.json({ ok: true });
  } catch (error) {
    console.error("ERROR DELETE /categorias/:id:", error);
    return res.status(500).json({ ok: false, error: "Error eliminando categoría" });
  }
});

export default router;
