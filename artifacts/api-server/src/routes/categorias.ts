import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const DATA_FILE  = path.join(__dirname, "../../data/categorias.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function leer(): any[] {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8")); }
  catch { return []; }
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
function slugify(str: string): string {
  return str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

const router = Router();

router.get("/categorias", (_req, res) => {
  res.json(leer());
});

router.post("/admin/categoria", (req, res) => {
  if (!auth(req, res)) return;
  const lista = leer();
  const id = slugify(req.body.nombre ?? "cat") + "_" + Date.now().toString(36);
  const nueva = {
    id,
    nombre: req.body.nombre ?? "",
    imagen: req.body.imagen ?? "",
    emoji:  req.body.emoji  ?? "🛍️",
    color:  req.body.color  ?? "#1976d2",
  };
  lista.push(nueva);
  guardar(lista);
  res.json({ ok: true, categoria: nueva });
});

router.put("/admin/categoria/:id", (req, res) => {
  if (!auth(req, res)) return;
  const lista = leer();
  const idx = lista.findIndex((c: any) => c.id === req.params.id);
  if (idx === -1) { res.status(404).json({ ok: false, error: "No encontrada" }); return; }
  lista[idx] = { ...lista[idx], ...req.body };
  guardar(lista);
  res.json({ ok: true, categoria: lista[idx] });
});

router.delete("/admin/categoria/:id", (req, res) => {
  if (!auth(req, res)) return;
  const lista = leer().filter((c: any) => c.id !== req.params.id);
  guardar(lista);
  res.json({ ok: true });
});

export default router;
