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

function slugify(texto: string): string {
  return String(texto || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/\s+/g, "_")
    .replace(/[^a-z0-9_]/g, "")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "") || "otro";
}

function normalizarCategoria(body: any, actual?: any) {
  const nombre = String(body?.nombre ?? actual?.nombre ?? "").trim();
  const emoji = String(body?.emoji ?? actual?.emoji ?? "🛍️").trim() || "🛍️";

  let imagen = String(actual?.imagen ?? actual?.foto ?? "").trim();

  if (body?.imagen !== undefined) imagen = String(body.imagen || "").trim();
  else if (body?.foto !== undefined) imagen = String(body.foto || "").trim();
  else if (body?.image !== undefined) imagen = String(body.image || "").trim();
  else if (body?.imageUrl !== undefined) imagen = String(body.imageUrl || "").trim();

  const slug = String(body?.slug ?? actual?.slug ?? slugify(nombre)).trim() || slugify(nombre);

  return {
    id: String(actual?.id ?? Date.now().toString()),
    slug,
    nombre,
    emoji,
    imagen
  };
}

// OBTENER CATEGORIAS
router.get("/categorias", (_req, res) => {
  res.json(leer());
});

// CREAR CATEGORIA
router.post("/categorias", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const nueva = normalizarCategoria(req.body ?? {});

  if (!nueva.nombre) {
    return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
  }

  const slugYaExiste = categorias.some((c: any) => String(c.slug) === String(nueva.slug));
  if (slugYaExiste) {
    nueva.slug = `${nueva.slug}_${Date.now()}`;
  }

  categorias.push(nueva);
  guardar(categorias);

  return res.json({ ok: true, categoria: nueva });
});

// EDITAR CATEGORIA
router.put("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const id = String(req.params.id);
  const index = categorias.findIndex((c: any) => String(c.id) === id);

  if (index === -1) {
    return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
  }

  const actual = categorias[index];
  const actualizada = normalizarCategoria(req.body ?? {}, actual);

  if (!actualizada.nombre) {
    return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
  }

  const slugDuplicado = categorias.some(
    (c: any, i: number) => i !== index && String(c.slug) === String(actualizada.slug)
  );

  if (slugDuplicado) {
    actualizada.slug = `${actualizada.slug}_${Date.now()}`;
  }

  categorias[index] = actualizada;
  guardar(categorias);

  return res.json({ ok: true, categoria: actualizada });
});

// ELIMINAR CATEGORIA
router.delete("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const nuevas = categorias.filter((c: any) => String(c.id) !== String(req.params.id));

  if (nuevas.length === categorias.length) {
    return res.status(404).json({ ok: false, error: "Categoría no encontrada" });
  }

  guardar(nuevas);
  return res.json({ ok: true });
});

export default router;
