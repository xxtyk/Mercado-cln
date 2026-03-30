import { Router } from "express";

import health from "./health.js";
import productos from "./productos.js";
import categorias from "./categorias.js";
import upload from "./upload.js";
import webhook from "./webhook-proxy.js";

const router = Router();

router.use("/", health);
router.use("/", productos);
router.use("/", categorias);
router.use("/", upload);
router.use("/", webhook);

export default router;
