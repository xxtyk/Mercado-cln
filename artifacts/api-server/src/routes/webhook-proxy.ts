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
    const { cliente, telefono, direccion, nota, vendedor, vendedor_wa, tipo_entrega, productos, total, pago } = req.body;

    const lineas = Array.isArray(productos)
      ? productos.map((p: { nombre: string; cantidad: number; subtotal: number }) =>
          `  • ${p.nombre} x${p.cantidad} = $${p.subtotal}.00`
        ).join("\n")
      : "";

    const subtotalProductos = Array.isArray(productos)
      ? productos.reduce((s: number, p: { subtotal: number }) => s + p.subtotal, 0)
      : total;
    const costoEnvio = tipo_entrega === "Envío a domicilio" ? 40 : 0;
    const resumenTotal = costoEnvio > 0
      ? `$${subtotalProductos}.00 productos + $${costoEnvio}.00 envío = *$${total}.00*`
      : `*$${total}.00*`;

    const mensajeGrupo =
      `🛒 *NUEVO PEDIDO*\n` +
      `👤 *Cliente:* ${cliente}\n` +
      `📱 *WhatsApp cliente:* ${normalizarTelefono(telefono)}\n` +
      `📍 *Dirección:* ${direccion}\n` +
      `🧑‍💼 *Vendedor:* ${vendedor}\n` +
      `📦 *Entrega:* ${tipo_entrega}\n\n` +
      `🧾 *Productos:*\n${lineas}\n\n` +
      `💰 *Total:* ${resumenTotal}\n` +
      `💵 *Pago:* ${pago}` +
      (nota ? `\n📝 *Nota:* ${nota}` : "");

    const mensajeCliente =
      `🛒⚫🔵 *MERCADO EN LÍNEA CULIACÁN* 🔵⚫🛒\n\n` +
      `¡Gracias por su compra, *${cliente}*! ✅\n\n` +
      `👤 *Su vendedor es:* ${vendedor}\n` +
      `📲 Para dudas o aclaraciones sobre su pedido escríbale directo aquí:\n` +
      `👉 https://wa.me/${vendedor_wa}\n\n` +
      `━━━━━━━━━━━━━━━━━━\n` +
      `🕛 Empezamos a entregar *de medio día en adelante*.\n\n` +
      `🛵 Espere el mensaje del *repartidor* por WhatsApp para coordinar su entrega.\n` +
      `━━━━━━━━━━━━━━━━━━\n\n` +
      `¡Gracias por elegir *Mercado en Línea Culiacán*! 🙌`;

    const telefonoNormalizado = normalizarTelefono(telefono);

    const mensajeVendedor =
      `📦 *PEDIDO PARA RECOGER EN BODEGA*\n\n` +
      `👤 *Cliente:* ${cliente}\n` +
      `📱 *WhatsApp:* ${telefonoNormalizado}\n\n` +
      `🧾 *Productos:*\n${lineas}\n\n` +
      `💰 *Total:* *$${total}.00*\n` +
      `💵 *Pago:* ${pago}\n` +
      (nota ? `📝 *Nota:* ${nota}\n` : "") +
      `\n_El cliente pasará a recoger. Favor de coordinar hora y ubicación._`;

    const envios: Promise<Response>[] = [
      enviarWA(GRUPO_ENVIO_ID, mensajeGrupo),
      enviarWA(`${telefonoNormalizado}@c.us`, mensajeCliente),
    ];

    if (tipo_entrega === "Recoger en bodega" && vendedor_wa) {
      envios.push(enviarWA(`${normalizarTelefono(vendedor_wa)}@c.us`, mensajeVendedor));
    }

    const [resGrupo, resCliente, resVendedor] = await Promise.all(envios);

    const dataGrupo   = await resGrupo.json();
    const dataCliente = await resCliente.json();
    const dataVendedor = resVendedor ? await resVendedor.json() : null;

    res.status(200).json({ ok: true, grupo: dataGrupo, cliente: dataCliente, vendedor: dataVendedor });
  } catch (err) {
    res.status(500).json({ ok: false, error: String(err) });
  }
});

export default router;
