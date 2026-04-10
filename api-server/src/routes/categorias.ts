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
    res.status(401).json({ ok: false });
    return false;
  }
  return true;
}

// 🔥 GENERAR SLUG AUTOMÁTICO
function generarSlug(nombre: string) {
  return nombre
    .toLowerCase()
    .replaceAll(" ", "_")
    .replace(/[^\w_]/g, "");
}

// GET
router.get("/categorias", (_req, res) => {
  res.json(leer());
});

// POST
router.post("/categorias", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();

  const nombre = String(req.body?.nombre || "").trim();
  const emoji = String(req.body?.emoji || "🛍️").trim();

  let imagen = req.body?.imagen || "";

  if (!nombre) {
    return res.status(400).json({ ok: false });
  }

  const nueva = {
    id: Date.now().toString(),
    slug: generarSlug(nombre), // 🔥 CLAVE
    nombre,
    emoji,
    imagen
  };

  categorias.push(nueva);
  guardar(categorias);

  res.json({ ok: true, categoria: nueva });
});

// PUT 🔥 NECESARIO PARA EDITAR
router.put("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const i = categorias.findIndex((c: any) => String(c.id) === String(req.params.id));

  if (i === -1) {
    return res.status(404).json({ ok: false });
  }

  const nombre = req.body?.nombre || categorias[i].nombre;

  categorias[i] = {
    ...categorias[i],
    nombre,
    slug: generarSlug(nombre), // 🔥 ACTUALIZA SLUG
    emoji: req.body?.emoji ?? categorias[i].emoji,
    imagen: req.body?.imagen ?? categorias[i].imagen
  };

  guardar(categorias);

  res.json({ ok: true, categoria: categorias[i] });
});

export default router;
