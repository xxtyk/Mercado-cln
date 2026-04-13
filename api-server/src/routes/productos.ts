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

function normalizarProducto(body: any, id: number | string, actual?: any) {
  const categoria = String(
    body.categoria ??
    actual?.categoria ??
    "otro"
  ).trim();

  const categoria_id = String(
    body.categoria_id ??
    actual?.categoria_id ??
    ""
  ).trim();

  return {
    id: Number(id),
    codigo: String(body.codigo ?? actual?.codigo ?? "").trim(),
    nombre: String(body.nombre ?? actual?.nombre ?? "").trim(),
    descripcion: String(body.descripcion ?? actual?.descripcion ?? "").trim(),
    imagen: String(
      body.imagen ??
      body.foto ??
      body.image ??
      actual?.imagen ??
      ""
    ).trim(),
    etiqueta: String(body.etiqueta ?? actual?.etiqueta ?? "Nuevo").trim(),
    precio: body.precio !== undefined ? Number(body.precio) : Number(actual?.precio ?? 0),
    categoria,
    categoria_id,
    activo: body.activo !== undefined
      ? Boolean(body.activo)
      : (actual?.activo !== undefined ? Boolean(actual.activo) : true)
  };
}

router.get("/productos", async (_req, res) => {
  try {
    const result = await pool.query("SELECT * FROM productos ORDER BY id DESC");
    res.json(result.rows);
  } catch (error) {
    console.error("ERROR GET /productos:", error);
    res.status(500).json({ ok: false, error: "Error obteniendo productos" });
  }
});

router.get("/productos/:id", async (req, res) => {
  try {
    const result = await pool.query(
      "SELECT * FROM productos WHERE id = $1 LIMIT 1",
      [Number(req.params.id)]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ ok: false, error: "Producto no encontrado" });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    console.error("ERROR GET /productos/:id:", error);
    return res.status(500).json({ ok: false, error: "Error obteniendo producto" });
  }
});

router.post("/productos", async (req: any, res) => {
  try {
    const max = await pool.query("SELECT COALESCE(MAX(id), 0) AS max_id FROM productos");
    const nuevo = normalizarProducto(req.body ?? {}, Number(max.rows[0].max_id) + 1);

    if (!nuevo.nombre) {
      return res.status(400).json({ ok: false, error: "Falta nombre" });
    }

    if (Number.isNaN(nuevo.precio)) {
      return res.status(400).json({ ok: false, error: "Precio inválido" });
    }

    await pool.query(
      `
      INSERT INTO productos
      (id, codigo, nombre, descripcion, imagen, etiqueta, precio, categoria, categoria_id, activo)
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
      `,
      [
        nuevo.id,
        nuevo.codigo,
        nuevo.nombre,
        nuevo.descripcion,
        nuevo.imagen,
        nuevo.etiqueta,
        nuevo.precio,
        nuevo.categoria,
        nuevo.categoria_id,
        nuevo.activo
      ]
    );

    return res.json({ ok: true, producto: nuevo });
  } catch (error) {
    console.error("ERROR POST /productos:", error);
    return res.status(500).json({ ok: false, error: "Error guardando producto" });
  }
});

router.put("/productos/:id", async (req: any, res) => {
  try {
    const id = Number(req.params.id);

    const actualResult = await pool.query(
      "SELECT * FROM productos WHERE id = $1 LIMIT 1",
      [id]
    );

    if (actualResult.rows.length === 0) {
      return res.status(404).json({ ok: false, error: "Producto no encontrado" });
    }

    const actualizado = normalizarProducto(req.body ?? {}, id, actualResult.rows[0]);

    await pool.query(
      `
      UPDATE productos
      SET codigo = $1,
          nombre = $2,
          descripcion = $3,
          imagen = $4,
          etiqueta = $5,
          precio = $6,
          categoria = $7,
          categoria_id = $8,
          activo = $9
      WHERE id = $10
      `,
      [
        actualizado.codigo,
        actualizado.nombre,
        actualizado.descripcion,
        actualizado.imagen,
        actualizado.etiqueta,
        actualizado.precio,
        actualizado.categoria,
        actualizado.categoria_id,
        actualizado.activo,
        id
      ]
    );

    return res.json({ ok: true, producto: actualizado });
  } catch (error) {
    console.error("ERROR PUT /productos/:id:", error);
    return res.status(500).json({ ok: false, error: "Error actualizando producto" });
  }
});

router.delete("/productos/:id", async (req: any, res) => {
  try {
    const result = await pool.query(
      "DELETE FROM productos WHERE id = $1",
      [Number(req.params.id)]
    );

    if ((result.rowCount ?? 0) === 0) {
      return res.status(404).json({ ok: false, error: "Producto no encontrado" });
    }

    return res.json({ ok: true });
  } catch (error) {
    console.error("ERROR DELETE /productos/:id:", error);
    return res.status(500).json({ ok: false, error: "Error eliminando producto" });
  }
});

router.post("/admin/producto", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const max = await pool.query("SELECT COALESCE(MAX(id), 0) AS max_id FROM productos");
    const nuevo = normalizarProducto(req.body ?? {}, Number(max.rows[0].max_id) + 1);

    if (!nuevo.nombre) {
      return res.status(400).json({ ok: false, error: "Falta nombre" });
    }

    if (Number.isNaN(nuevo.precio)) {
      return res.status(400).json({ ok: false, error: "Precio inválido" });
    }

    await pool.query(
      `
      INSERT INTO productos
      (id, codigo, nombre, descripcion, imagen, etiqueta, precio, categoria, categoria_id, activo)
      VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
      `,
      [
        nuevo.id,
        nuevo.codigo,
        nuevo.nombre,
        nuevo.descripcion,
        nuevo.imagen,
        nuevo.etiqueta,
        nuevo.precio,
        nuevo.categoria,
        nuevo.categoria_id,
        nuevo.activo
      ]
    );

    return res.json({ ok: true, producto: nuevo });
  } catch (error) {
    console.error("ERROR POST /admin/producto:", error);
    return res.status(500).json({ ok: false, error: "Error guardando producto" });
  }
});

router.put("/admin/producto/:id", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const id = Number(req.params.id);

    const actualResult = await pool.query(
      "SELECT * FROM productos WHERE id = $1 LIMIT 1",
      [id]
    );

    if (actualResult.rows.length === 0) {
      return res.status(404).json({ ok: false, error: "Producto no encontrado" });
    }

    const actualizado = normalizarProducto(req.body ?? {}, id, actualResult.rows[0]);

    await pool.query(
      `
      UPDATE productos
      SET codigo = $1,
          nombre = $2,
          descripcion = $3,
          imagen = $4,
          etiqueta = $5,
          precio = $6,
          categoria = $7,
          categoria_id = $8,
          activo = $9
      WHERE id = $10
      `,
      [
        actualizado.codigo,
        actualizado.nombre,
        actualizado.descripcion,
        actualizado.imagen,
        actualizado.etiqueta,
        actualizado.precio,
        actualizado.categoria,
        actualizado.categoria_id,
        actualizado.activo,
        id
      ]
    );

    return res.json({ ok: true, producto: actualizado });
  } catch (error) {
    console.error("ERROR PUT /admin/producto/:id:", error);
    return res.status(500).json({ ok: false, error: "Error actualizando producto" });
  }
});

router.delete("/admin/producto/:id", async (req: any, res) => {
  if (!autenticado(req, res)) return;

  try {
    const result = await pool.query(
      "DELETE FROM productos WHERE id = $1",
      [Number(req.params.id)]
    );

    if ((result.rowCount ?? 0) === 0) {
      return res.status(404).json({ ok: false, error: "Producto no encontrado" });
    }

    return res.json({ ok: true });
  } catch (error) {
    console.error("ERROR DELETE /admin/producto/:id:", error);
    return res.status(500).json({ ok: false, error: "Error eliminando producto" });
  }
});

export default router;
