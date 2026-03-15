import { Router } from "express";

const GREEN_API_INSTANCE = "7107547964";
const GREEN_API_TOKEN    = "1e6ec2470cfe4808a27cee392009c87bda99eaf03fa64a70b6";
const GREEN_API_URL      = `https://7107.api.greenapi.com/waInstance${GREEN_API_INSTANCE}/sendMessage/${GREEN_API_TOKEN}`;
const GRUPO_ENVIO_ID     = "120363423760711292@g.us";

const router = Router();

router.post("/webhook-pedido", async (req, res) => {
  try {
    const { cliente, direccion, vendedor, tipo_entrega, productos, total, pago } = req.body;

    const lineas = Array.isArray(productos)
      ? productos.map((p: { nombre: string; cantidad: number; subtotal: number }) =>
          `  • ${p.nombre} x${p.cantidad} = $${p.subtotal}.00`
        ).join("\n")
      : "";

    const mensaje =
      `🛒 *NUEVO PEDIDO*\n` +
      `👤 *Cliente:* ${cliente}\n` +
      `📍 *Dirección:* ${direccion}\n` +
      `🧑‍💼 *Vendedor:* ${vendedor}\n` +
      `📦 *Entrega:* ${tipo_entrega}\n\n` +
      `🧾 *Productos:*\n${lineas}\n\n` +
      `💰 *Total: $${total}.00*\n` +
      `💵 *Pago:* ${pago}`;

    const response = await fetch(GREEN_API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chatId: GRUPO_ENVIO_ID, message: mensaje }),
    });

    const data = await response.json();
    res.status(200).json({ ok: true, status: response.status, data });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

export default router;
