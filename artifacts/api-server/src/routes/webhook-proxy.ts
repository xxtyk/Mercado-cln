import { Router } from "express";

const GREEN_API_INSTANCE = "7107547964";
const GREEN_API_TOKEN    = "1e6ec2470cfe4808a27cee392009c87bda99eaf03fa64a70b6";
const GREEN_API_URL      = `https://7107.api.greenapi.com/waInstance${GREEN_API_INSTANCE}/sendMessage/${GREEN_API_TOKEN}`;
const GRUPO_ENVIO_ID     = "120363423760711292@g.us";

const router = Router();

function normalizarTelefono(tel: string): string {
  const digits = tel.replace(/\D/g, "");
  if (digits.length === 10) return `52${digits}`;
  return digits;
}

async function enviarWA(chatId: string, message: string) {
  return fetch(GREEN_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chatId, message }),
  });
}

router.post("/webhook-pedido", async (req, res) => {
  try {
    const { cliente, telefono, direccion, nota, vendedor, tipo_entrega, productos, total, pago } = req.body;

    const lineas = Array.isArray(productos)
      ? productos.map((p: { nombre: string; cantidad: number; subtotal: number }) =>
          `  • ${p.nombre} x${p.cantidad} = $${p.subtotal}.00`
        ).join("\n")
      : "";

    const mensajeGrupo =
      `🛒 *NUEVO PEDIDO*\n` +
      `👤 *Cliente:* ${cliente}\n` +
      `📱 *WhatsApp cliente:* https://wa.me/${normalizarTelefono(telefono)}\n` +
      `📍 *Dirección:* ${direccion}\n` +
      `🧑‍💼 *Vendedor:* ${vendedor}\n` +
      `📦 *Entrega:* ${tipo_entrega}\n\n` +
      `🧾 *Productos:*\n${lineas}\n\n` +
      `💰 *Total: $${total}.00*\n` +
      `💵 *Pago:* ${pago}` +
      (nota ? `\n📝 *Nota:* ${nota}` : "");

    const mensajeCliente =
      `*MERCADO EN LÍNEA CULIACÁN* 🛒🔵⚫\n\n` +
      `¡Muchas gracias por tu compra, ${cliente}! Tu pedido ha sido recibido con éxito. ✅\n\n` +
      `👤 *Te atendió:* ${vendedor}\n` +
      `_(Para tus próximos pedidos, ¡no dudes en contactarle directamente!)_\n\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `⚠️ *INFORMACIÓN IMPORTANTE SOBRE TU ENTREGA:*\n\n` +
      `🛵 *EL REPARTIDOR TE CONTACTARÁ POR WHATSAPP* para coordinar los detalles exactos de la entrega y confirmar tu ubicación.\n\n` +
      `🕛 *HORARIOS DE ENTREGA:* Recuerda que comenzamos con las rutas de reparto *después del medio día*.\n` +
      `━━━━━━━━━━━━━━━━━━\n\n` +
      `¡Gracias por elegir *Mercado en Línea Culiacán*! 🙌\n` +
      `_Calidad y frescura hasta tu hogar._`;

    const telefonoNormalizado = normalizarTelefono(telefono);

    const [resGrupo, resCliente] = await Promise.all([
      enviarWA(GRUPO_ENVIO_ID, mensajeGrupo),
      enviarWA(`${telefonoNormalizado}@c.us`, mensajeCliente),
    ]);

    const dataGrupo   = await resGrupo.json();
    const dataCliente = await resCliente.json();

    res.status(200).json({ ok: true, grupo: dataGrupo, cliente: dataCliente });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

export default router;
