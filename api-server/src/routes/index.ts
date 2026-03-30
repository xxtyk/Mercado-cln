
import { Router } from "express";

import health from "./health";
import productos from "./productos";
import categorias from "./categorias";
import upload from "./upload";
import webhook from "./webhook-proxy";

const router = Router();

router.use("/", health);
router.use("/", productos);
router.use("/", categorias);
router.use("/", upload);
router.use("/", webhook);

export default router;
