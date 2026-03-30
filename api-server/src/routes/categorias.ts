
import { Router } from "express";
import fs from "fs";
import path from "path";

const router = Router();

const DATA_FILE = path.join(process.cwd(), "categorias.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "1234";

// leer
function leer() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8"));
  } catch {
    return [];
  }
}

// guardar
function guardar(data: any[]) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// auth
function auth(req: any, res: any) {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false });
    return false;
  }
  return true;
}

// GET categorias
router.get("/categorias", (_req, res) => {
  res.json(leer());
});

// POST categoria
router.post("/admin/categoria", (req, res) => {
  if (!auth(req, res)) return;

  const lista = leer();

  const nueva = {
    id: Date.now().toString(),
    nombre: req.body.nombre ?? "",
    imagen: req.body.imagen ?? "",
    emoji: req.body.emoji ?? "🛍️",
    color: req.body.color ?? "#1976d2",
  };

  lista.push(nueva);
  guardar(lista);

  res.json({ ok: true });
});

// PUT categoria
router.put("/admin/categoria/:id", (req, res) => {
  if (!auth(req, res)) return;

  const lista = leer();

  const idx = lista.findIndex((c: any) => c.id == req.params.id);

  if (idx === -1) return res.json({ ok: false });

  lista[idx] = { ...lista[idx], ...req.body };

  guardar(lista);

  res.json({ ok: true });
});

// DELETE categoria
router.delete("/admin/categoria/:id", (req, res) => {
  if (!auth(req, res)) return;

  const lista = leer().filter(
    (c: any) => c.id != req.params.id
  );

  guardar(lista);

  res.json({ ok: true });
});

export default router;
