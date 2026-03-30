import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const router = Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_FILE = path.join(__dirname, "../../data/productos.json");
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

function autenticado(req: any, res: any): boolean {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

router.get("/productos", (_req, res) => {
  res.json(leer());
});

router.get("/productos/:id", (req, res) => {
  const lista = leer();
  const id = Number(req.params.id);
  const producto = lista.find((p: any) => Number(p.id) === id);

  if (!producto) {
    return res.status(404).json({ ok: false, error: "Producto no encontrado" });
  }

  return res.json(producto);
});

router.post("/admin/producto", (req: any, res) => {
  if (!autenticado(req, res)) return;

  const lista = leer();
  const maxId = lista.reduce((m: number, p: any) => Math.max(m, Number(p.id) || 0), 0);

  const nuevo = {
    id: maxId + 1,
    codigo: req.body.codigo ?? "",
    nombre: req.body.nombre ?? "",
    descripcion: req.body.descripcion ?? "",
    imagen: req.body.imagen ?? "",
    etiqueta: req.body.etiqueta ?? "Nuevo",
    precio: Number(req.body.precio ?? 0),
    categoria: req.body.categoria ?? ""
  };

  lista.push(nuevo);
  guardar(lista);

  return res.json({ ok: true, producto: nuevo });
});

router.put("/admin/producto/:id", (req: any, res) => {
  if (!autenticado(req, res)) return;

  const lista = leer();
  const id = Number(req.params.id);
  const i = lista.findIndex((p: any) => Number(p.id) === id);

  if (i === -1) {
    return res.status(404).json({ ok: false, error: "Producto no encontrado" });
  }

  const actual = lista[i];

  lista[i] = {
    ...actual,
    codigo: req.body.codigo !== undefined ? req.body.codigo : actual.codigo,
    nombre: req.body.nombre !== undefined ? req.body.nombre : actual.nombre,
    descripcion: req.body.descripcion !== undefined ? req.body.descripcion : actual.descripcion,
    imagen: req.body.imagen !== undefined ? req.body.imagen : actual.imagen,
    etiqueta: req.body.etiqueta !== undefined ? req.body.etiqueta : actual.etiqueta,
    precio: req.body.precio !== undefined ? Number(req.body.precio) : actual.precio,
    categoria: req.body.categoria !== undefined ? req.body.categoria : actual.categoria
  };

  guardar(lista);

  return res.json({ ok: true, producto: lista[i] });
});

router.delete("/admin/producto/:id", (req: any, res) => {
  if (!autenticado(req, res)) return;

  const lista = leer();
  const nuevaLista = lista.filter((p: any) => Number(p.id) !== Number(req.params.id));

  if (nuevaLista.length === lista.length) {
    return res.status(404).json({ ok: false, error: "Producto no encontrado" });
  }

  guardar(nuevaLista);

  return res.json({ ok: true });
});

export default router;
