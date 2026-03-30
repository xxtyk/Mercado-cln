
import { Router } from "express";
import fs from "fs";
import path from "path";

const router = Router();

const DATA_FILE = path.join(process.cwd(), "productos.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "1234";

// leer productos
function leer() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8"));
  } catch {
    return [];
  }
}

// guardar productos
function guardar(data: any[]) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// auth simple
function auth(req: any, res: any) {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false });
    return false;
  }
  return true;
}

// GET productos
router.get("/productos", (_req, res) => {
  res.json(leer());
});

// POST producto
router.post("/admin/producto", (req, res) => {
  if (!auth(req, res)) return;

  const lista = leer();
  const id = Date.now();

  const nuevo = {
    id,
    ...req.body,
  };

  lista.push(nuevo);
  guardar(lista);

  res.json({ ok: true });
});

// DELETE producto
router.delete("/admin/producto/:id", (req, res) => {
  if (!auth(req, res)) return;

  const lista = leer().filter(
    (p: any) => p.id != req.params.id
  );

  guardar(lista);

  res.json({ ok: true });
});

export default router;
