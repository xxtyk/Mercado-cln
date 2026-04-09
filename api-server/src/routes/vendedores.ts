import { Router } from "express";

const router = Router();

let vendedores = [];

router.get("/vendedores", (_req, res) => {
  res.json(vendedores);
});

router.post("/vendedores", (req, res) => {
  vendedores.unshift({
    id: Date.now().toString(),
    nombre: req.body.nombre
  });

  res.json({ ok: true });
});

router.delete("/vendedores/:id", (req, res) => {
  vendedores = vendedores.filter(v => v.id !== req.params.id);
  res.json({ ok: true });
});

export default router;
