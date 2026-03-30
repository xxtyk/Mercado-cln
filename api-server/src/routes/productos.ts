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
  const auth = req.headers.authorization ?? "";
  if (auth !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

function normalizarProducto(body: any, id: number, actual?: any) {
  return {
    id,
    codigo: body.codigo ?? actual?.codigo ?? "",
    nombre: body.nombre ?? actual?.nombre ?? "",
    descripcion: body.descripcion ?? actual?.descripcion ?? "",
    imagen: body.imagen ?? body.foto ?? body.image ?? actual?.imagen ?? "",
    etiqueta: body.etiqueta ?? actual?.etiqueta ?? "Nuevo",
    precio: body.precio !== undefined ? Number(body.precio) : Number(actual?.precio ?? 0),
    categoria:
      body.categoria ??
      body.categoria_id ??
      actual?.categoria ??
      actual?.categoria_id ??
      "",
    categoria_id:
      body.categoria_id ??
      body.categoria ??
      actual?.categoria_id ??
      actual?.categoria ??
      ""
  };
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

/* CREAR PRODUCTO DESDE PANEL */
router.post("/productos", (req: any, res) => {
  const lista = leer();
  const maxId = lista.reduce((m: number, p: any) => Math.max(m, Number(p.id) || 0), 0);

  const nuevo = normalizarProducto(req.body ?? {}, maxId + 1);

  if (!nuevo.nombre) {
    return res.status(400).json({ ok: false, error: "Falta nombre" });
  }

  if (!nuevo.precio && nuevo.precio !== 0) {
    return res.status(400).json({ ok: false, error: "Falta precio" });
  }

  lista.push(nuevo);
  guardar(lista);

  return res.json({ ok: true, producto: nuevo });
});

/* EDITAR PRODUCTO DESDE PANEL */
router.put("/productos/:id", (req: any, res) => {
  const lista = leer();
  const id = Number(req.params.id);
  const i = lista.findIndex((p: any) => Number(p.id) === id);

  if (i === -1) {
    return res.status(404).json({ ok: false, error: "Producto no encontrado" });
  }

  lista[i] = normalizarProducto(req.body ?? {}, id, lista[i]);
  guardar(lista);

  return res.json({ ok: true, producto: lista[i] });
});

/* ELIMINAR PRODUCTO DESDE PANEL */
router.delete("/productos/:id", (req: any, res) => {
  const lista = leer();
  const nuevaLista = lista.filter((p: any) => Number(p.id) !== Number(req.params.id));

  if (nuevaLista.length === lista.length) {
    return res.status(404).json({ ok: false, error: "Producto no encontrado" });
  }

  guardar(nuevaLista);

  return res.json({ ok: true });
});

/* RUTAS VIEJAS PARA NO ROMPER NADA */
router.post("/admin/producto", (req: any, res) => {
  if (!autenticado(req, res)) return;

  const lista = leer();
  const maxId = lista.reduce((m: number, p: any) => Math.max(m, Number(p.id) || 0), 0);
  const nuevo = normalizarProducto(req.body ?? {}, maxId + 1);

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

  lista[i] = normalizarProducto(req.body ?? {}, id, lista[i]);
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
