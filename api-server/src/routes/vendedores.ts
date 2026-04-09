import { Router } from "express";

const router = Router();

let vendedores = [
  { id: "1", nombre: "Mercado en Línea Culiacán" },
  { id: "2", nombre: "Hector" },
  { id: "3", nombre: "Silvia" },
  { id: "4", nombre: "Juan" },
  { id: "5", nombre: "Cristian" },
  { id: "6", nombre: "Amayrani" },
  { id: "7", nombre: "Brisa" },
  { id: "8", nombre: "Claudia" },
  { id: "9", nombre: "Natalia" }
];

// OBTENER VENDEDORES
router.get("/vendedores", (_req, res) => {
  res.json(vendedores);
});

// AGREGAR VENDEDOR
router.post("/vendedores", (req, res) => {
  const nombre = String(req.body?.nombre || "").trim();

  if (!nombre) {
    return res.status(400).json({ error: "Falta nombre" });
  }

  const nuevo = {
    id: Date.now().toString(),
    nombre
  };

  vendedores.unshift(nuevo);

  res.json({ ok: true, vendedor: nuevo });
});

// EDITAR VENDEDOR
router.put("/vendedores/:id", (req, res) => {
  const nombre = String(req.body?.nombre || "").trim();

  if (!nombre) {
    return res.status(400).json({ error: "Falta nombre" });
  }

  vendedores = vendedores.map(v =>
    v.id === req.params.id ? { ...v, nombre } : v
  );

  res.json({ ok: true });
});

// ELIMINAR VENDEDOR
router.delete("/vendedores/:id", (req, res) => {
  vendedores = vendedores.filter(v => v.id !== req.params.id);
  res.json({ ok: true });
});

export default router;
