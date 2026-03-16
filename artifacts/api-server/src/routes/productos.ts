import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const DATA_FILE  = path.join(__dirname, "../../data/productos.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function leer(): any[] {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8")); }
  catch { return []; }
}

function guardar(data: any[]) {
  fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), "utf-8");
}

function autenticado(req: any, res: any): boolean {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

const router = Router();

router.get("/productos", (_req, res) => {
  res.json(leer());
});

router.post("/admin/producto", (req, res) => {
  if (!autenticado(req, res)) return;
  const lista = leer();
  const maxId = lista.reduce((m: number, p: any) => Math.max(m, p.id ?? 0), 0);
  const nuevo = {
    id:          maxId + 1,
    codigo:      req.body.codigo      ?? "",
    nombre:      req.body.nombre      ?? "",
    descripcion: req.body.descripcion ?? "",
    imagen:      req.body.imagen      ?? "",
    etiqueta:    req.body.etiqueta    ?? "Nuevo",
    precio:      Number(req.body.precio ?? 0),
    categoria:   req.body.categoria   ?? "",
  };
  lista.push(nuevo);
  guardar(lista);
  res.json({ ok: true, producto: nuevo });
});

router.delete("/admin/producto/:id", (req, res) => {
  if (!autenticado(req, res)) return;
  const lista = leer().filter((p: any) => p.id !== Number(req.params.id));
  guardar(lista);
  res.json({ ok: true });
});

export default router;
