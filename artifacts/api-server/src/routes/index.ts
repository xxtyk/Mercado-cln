import { Router, type IRouter } from "express";
import healthRouter      from "./health";
import webhookProxyRouter from "./webhook-proxy";
import productosRouter   from "./productos";
import uploadRouter      from "./upload";

const router: IRouter = Router();

router.use(healthRouter);
router.use(webhookProxyRouter);
router.use(productosRouter);
router.use(uploadRouter);

export default router;
