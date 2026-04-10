import { Router } from "express";

import health from "./health.js";
import productos from "./productos.js";
import categorias from "./categorias.js";
import upload from "./upload.js";
import webhook from "./webhook-proxy.js";
import pedidos from "./pedidos.js";
import vendedores from "./vendedores.js";

const router = Router();

// 🔥 RUTA DE PRUEBA
router.use("/health", health);

// 🔥 API PRINCIPAL
router.use("/", productos);
router.use("/", categorias);
router.use("/", upload);
router.use("/", webhook);
router.use("/", pedidos);
router.use("/", vendedores);

export default router;
