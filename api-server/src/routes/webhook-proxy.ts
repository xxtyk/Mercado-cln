import { Router } from "express";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const router = Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const DATA_FILE = path.join(__dirname, "../../data/pedidos.json");
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

function leerPedidos(): any[] {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, "utf-8"));
  } catch {
    return [];
  }
}

function guardarPedidos(data: any[]) {
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

router.get("/webhook-pedido", (_req, res) => {
  res.json(leerPedidos());
});

router.post("/webhook-pedido", (req, res) => {
  try {
    const data = req.body ?? {};
    const pedidos = leerPedidos();

    const nuevoPedido = {
      id: Date.now(),
      cliente: data.cliente ?? "Cliente",
      telefono: data.telefono ?? "",
      direccion: data.direccion ?? "",
      nota: data.nota ?? "",
      vendedor: data.vendedor ?? "",
      tipo_entrega: data.tipo_entrega ?? "",
      productos: Array.isArray(data.productos) ? data.productos : [],
      total: Number(data.total ?? 0),
      fecha: new Date().toISOString()
    };

    pedidos.unshift(nuevoPedido);
    guardarPedidos(pedidos);

    res.json({ ok: true, pedido: nuevoPedido });
  } catch (error: any) {
    res.status(500).json({
      ok: false,
      error: String(error?.message ?? error)
    });
  }
});

router.delete("/webhook-pedido/:id", (req: any, res) => {
  if (!auth(req, res)) return;

  const pedidos = leerPedidos();
  const id = String(req.params.id);
  const nuevos = pedidos.filter((p: any) => String(p.id) !== id);

  guardarPedidos(nuevos);
  res.json({ ok: true });
});

export default router;
