import { Router } from "express";

const router = Router();

let pedidos: any[] = [];

// VER PEDIDOS
router.get("/pedidos", (_req, res) => {
  res.json(pedidos);
});

// CREAR PEDIDO
router.post("/pedidos", (req, res) => {
  const pedido = {
    id: Date.now().toString(),
    ...req.body
  };

  pedidos.unshift(pedido);

  res.json({ ok: true, pedido });
});

// ELIMINAR PEDIDO
router.delete("/pedidos/:id", (req, res) => {
  pedidos = pedidos.filter((p) => p.id !== req.params.id);
  res.json({ ok: true });
});

// ENVIAR A WHATSAPP Y BORRAR
router.post("/pedidos/:id/whatsapp", (req, res) => {
  pedidos = pedidos.filter((p) => p.id !== req.params.id);
  res.json({ ok: true });
});

export default router;
