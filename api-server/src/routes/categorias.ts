import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const router = Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_FILE = path.join(__dirname, "../../data/categorias.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function leer(): any[] {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8"));
  } catch {
    return [];
  }
}

function guardar(data: any[]) {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), "utf-8");
}

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
router.get("/categorias", (_req, res) => {
  return res.json(leer());
});

// POST
router.post("/categorias", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();

  const nombre = String(req.body?.nombre || "").trim();
  const emoji = String(req.body?.emoji || "🛍️").trim() || "🛍️";
  const imagen = tomarImagen(req.body, "");

  if (!nombre) {
    return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
  }

  let slug = generarSlug(nombre);

  const slugRepetido = categorias.some((c: any) => String(c.slug || "") === slug);
  if (slugRepetido) {
    slug = `${slug}_${Date.now()}`;
  }

  const nueva = {
    id: Date.now().toString(),
    slug,
    nombre,
    emoji,
    imagen
  };

  categorias.push(nueva);
  guardar(categorias);

  return res.json({ ok: true, categoria: nueva });
});

// PUT
router.put("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const i = categorias.findIndex((c: any) => String(c.id) === String(req.params.id));

  if (i === -1) {
    return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
  }

  const nombre = String(req.body?.nombre || categorias[i].nombre || "").trim();
  const emoji = String(req.body?.emoji ?? categorias[i].emoji ?? "🛍️").trim() || "🛍️";
  const imagen = tomarImagen(req.body, categorias[i].imagen || "");

  if (!nombre) {
    return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
  }

  let slug = generarSlug(nombre);

  const slugRepetido = categorias.some(
    (c: any, index: number) =>
      index !== i && String(c.slug || "") === slug
  );

  if (slugRepetido) {
    slug = `${slug}_${Date.now()}`;
  }

  categorias[i] = {
    ...categorias[i],
    nombre,
    slug,
    emoji,
    imagen
  };

  guardar(categorias);

  return res.json({ ok: true, categoria: categorias[i] });
});

// DELETE
router.delete("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const nuevas = categorias.filter(
    (c: any) => String(c.id) !== String(req.params.id)
  );

  if (nuevas.length === categorias.length) {
    return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
  }

  guardar(nuevas);

  return res.json({ ok: true });
});

export default router;
