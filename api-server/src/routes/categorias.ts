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

router.get("/categorias", (_req, res) => {
  res.json(leer());
});

router.post("/categorias", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const { nombre, emoji, imagen } = req.body ?? {};

  if (!nombre || !String(nombre).trim()) {
    return res.status(400).json({ ok: false, error: "El nombre es obligatorio" });
  }

  const nueva = {
    id: Date.now().toString(),
    nombre: String(nombre).trim(),
    emoji: emoji ? String(emoji).trim() : "🛍️",
    imagen: imagen ? String(imagen).trim() : ""
  };

  categorias.push(nueva);
  guardar(categorias);

  return res.json({ ok: true, categoria: nueva });
});

router.delete("/categorias/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const categorias = leer();
  const nuevas = categorias.filter((c: any) => String(c.id) !== String(req.params.id));

  guardar(nuevas);
  return res.json({ ok: true });
});

export default router;
