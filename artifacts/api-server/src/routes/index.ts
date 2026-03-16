import { Router, type IRouter } from "express";
import healthRouter      from "./health";
import webhookProxyRouter from "./webhook-proxy";
import productosRouter   from "./productos";
import uploadRouter      from "./upload";
import categoriasRouter  from "./categorias";

const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

const router: IRouter = Router();

router.get("/admin/auth", (req, res) => {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false });
  } else {
    res.json({ ok: true });
  }
});

router.use(healthRouter);
router.use(webhookProxyRouter);
router.use(productosRouter);
router.use(uploadRouter);
router.use(categoriasRouter);

export default router;
