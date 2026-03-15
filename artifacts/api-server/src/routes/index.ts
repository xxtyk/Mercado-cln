import { Router, type IRouter } from "express";
import healthRouter from "./health";
import webhookProxyRouter from "./webhook-proxy";

const router: IRouter = Router();

router.use(healthRouter);
router.use(webhookProxyRouter);

export default router;
