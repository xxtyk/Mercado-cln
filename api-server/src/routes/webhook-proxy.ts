import { Router } from "express";

const router = Router();

const GREEN_API_INSTANCE = process.env.GREEN_API_INSTANCE ?? "";
const GREEN_API_TOKEN = process.env.GREEN_API_TOKEN ?? "";
const GREEN_API_CHAT_ID = process.env.GREEN_API_CHAT_ID ?? "";

const GREEN_API_URL = `https://7107.api.greenapi.com/waInstance${GREEN_API_INSTANCE}/sendMessage/${GREEN_API_TOKEN}`;

function soloLocal(tel: string): string {
  const digits = String(tel || "").replace(/\D/g, "");
  if (digits.length === 12 && digits.startsWith("52")) return digits.slice(2);
  if (digits.length === 13 && digits.startsWith("521")) return digits.slice(3);
  return digits;
}

function conPais(tel: string): string {
  const local = soloLocal(tel);
  return `52${local}`;
}

function chatId(tel: string): string {
  return `${conPais(tel)}@c.us`;
}

async function enviarWA(chatIdDestino: string, message: string) {
  return fetch(GREEN_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chatId: chatIdDestino,
      message,
    }),
  });
}

router.post("/webhook-pedido", async (req, res) => {
  try {
    const {
      cliente,
      telefono,
      direccion,
      nota,
      vendedor,
      vendedor_wa,
      tipo_entrega,
      productos,
      total,
      pago,
    } = req.body ?? {};

    const lista = Array.isArray(productos) ? productos : [];

    const lineas = lista
      .map((p: { nombre: string; cantidad: number; subtotal: number }) =>
        `• ${p.nombre} x${p.cantidad} = $${p.subtotal}.00`
      )
      .join("\n");

    const subtotalProductos = lista.reduce(
      (s: number, p: { subtotal: number }) => s + Number(p.subtotal || 0),
      0
    );

    const costoEnvio = tipo_entrega === "Envío a domicilio" ? 40 : 0;

    const resumenTotal =
      costoEnvio > 0
        ? `$${subtotalProductos}.00 productos + $${costoEnvio}.00 envío = $${total}.00`
        : `$${total}.00`;

    const mensajeGrupo =
      `🛒 NUEVO PEDIDO\n` +
      `👤 Cliente: ${cliente}\n` +
      `📱 WhatsApp cliente: ${soloLocal(telefono)}\n` +
      `📍 Dirección: ${direccion}\n` +
      `🧑‍💼 Vendedor: ${vendedor}\n` +
      `📦 Entrega: ${tipo_entrega}\n\n` +
      `🧾 Productos:\n${lineas}\n\n` +
      `💰 Total: ${resumenTotal}\n` +
      `💵 Pago: ${pago}` +
      (nota ? `\n📝 Nota: ${nota}` : "");

    const mensajeCliente =
      `🛒 MERCADO EN LÍNEA CULIACÁN\n\n` +
      `¡Gracias por su compra, ${cliente}! ✅\n\n` +
      `👤 Su vendedor es: ${vendedor}\n` +
      `📲 Para dudas o aclaraciones sobre su pedido escríbale directo aquí:\n` +
      `https://wa.me/${conPais(vendedor_wa)}\n\n` +
      `🛵 Espere el mensaje del repartidor por WhatsApp para coordinar su entrega.\n\n` +
      `¡Gracias por elegir Mercado en Línea Culiacán! 🙌`;

    const mensajeVendedor =
      `📦 PEDIDO PARA RECOGER EN BODEGA\n\n` +
      `👤 Cliente: ${cliente}\n` +
      `📱 WhatsApp: ${soloLocal(telefono)}\n\n` +
      `🧾 Productos:\n${lineas}\n\n` +
      `💰 Total: $${total}.00\n` +
      `💵 Pago: ${pago}` +
      (nota ? `\n📝 Nota: ${nota}` : "") +
      `\n\nEl cliente pasará a recoger. Favor de coordinar hora y ubicación.`;

    const envios: Promise<Response>[] = [];

    if (GREEN_API_INSTANCE && GREEN_API_TOKEN && GREEN_API_CHAT_ID) {
      envios.push(enviarWA(GREEN_API_CHAT_ID, mensajeGrupo));
    }

    if (telefono) {
      envios.push(enviarWA(chatId(telefono), mensajeCliente));
    }

    if (tipo_entrega === "Recoger en bodega" && vendedor_wa) {
      envios.push(enviarWA(chatId(vendedor_wa), mensajeVendedor));
    }

    const respuestas = await Promise.allSettled(envios);

    res.json({
      ok: true,
      respuestas,
    });
  } catch (error) {
    res.status(500).json({
      ok: false,
      error: String(error),
    });
  }
});

export default router;
