import { Router } from "express";

const router = Router();

const GREEN_API_INSTANCE = process.env.GREEN_API_INSTANCE ?? "";
const GREEN_API_TOKEN = process.env.GREEN_API_TOKEN ?? "";
const GREEN_API_CHAT_ID = process.env.GREEN_API_CHAT_ID ?? "";
const GREEN_API_HOST = process.env.GREEN_API_HOST ?? "https://7107.api.greenapi.com";

const GREEN_API_URL = `${GREEN_API_HOST}/waInstance${GREEN_API_INSTANCE}/sendMessage/${GREEN_API_TOKEN}`;

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

function chatIdTelefono(tel: string): string {
  return `${conPais(tel)}@c.us`;
}

async function enviarWA(chatIdDestino: string, message: string) {
  const respuesta = await fetch(GREEN_API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chatId: chatIdDestino,
      message
    })
  });

  const texto = await respuesta.text();

  return {
    ok: respuesta.ok,
    status: respuesta.status,
    body: texto
  };
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
      pago
    } = req.body ?? {};

    const lista = Array.isArray(productos) ? productos : [];

    const lineas = lista.length
      ? lista
          .map((p: any) => {
            const nombre = p?.nombre ?? "";
            const cantidad = Number(p?.cantidad ?? 0);
            const subtotal = Number(p?.subtotal ?? 0);
            return `• ${nombre} x${cantidad} = $${subtotal}.00`;
          })
          .join("\n")
      : "• Sin productos";

    const subtotalProductos = lista.reduce(
      (s: number, p: any) => s + Number(p?.subtotal ?? 0),
      0
    );

    const costoEnvio = tipo_entrega === "Envío a domicilio" ? 40 : 0;

    const resumenTotal =
      costoEnvio > 0
        ? `$${subtotalProductos}.00 productos + $${costoEnvio}.00 envío = $${Number(total ?? 0)}.00`
        : `$${Number(total ?? 0)}.00`;

    const mensajeGrupo =
      `🛒 NUEVO PEDIDO\n` +
      `👤 Cliente: ${cliente ?? ""}\n` +
      `📱 WhatsApp cliente: ${soloLocal(telefono ?? "")}\n` +
      `📍 Dirección: ${direccion ?? ""}\n` +
      `🧑‍💼 Vendedor: ${vendedor ?? ""}\n` +
      `📦 Entrega: ${tipo_entrega ?? ""}\n\n` +
      `🧾 Productos:\n${lineas}\n\n` +
      `💰 Total: ${resumenTotal}\n` +
      `💵 Pago: ${pago ?? ""}` +
      (nota ? `\n📝 Nota: ${nota}` : "");

    const mensajeCliente =
      `🛒 MERCADO EN LÍNEA CULIACÁN\n\n` +
      `¡Gracias por su compra, ${cliente ?? "cliente"}! ✅\n\n` +
      `👤 Su vendedor es: ${vendedor ?? ""}\n` +
      `📲 Para dudas o aclaraciones sobre su pedido escríbale directo aquí:\n` +
      (vendedor_wa ? `https://wa.me/${conPais(vendedor_wa)}` : "No disponible") +
      `\n\n🛵 Espere el mensaje del repartidor por WhatsApp para coordinar su entrega.\n\n` +
      `¡Gracias por elegir Mercado en Línea Culiacán! 🙌`;

    const mensajeVendedor =
      `📦 PEDIDO PARA RECOGER EN BODEGA\n\n` +
      `👤 Cliente: ${cliente ?? ""}\n` +
      `📱 WhatsApp: ${soloLocal(telefono ?? "")}\n\n` +
      `🧾 Productos:\n${lineas}\n\n` +
      `💰 Total: $${Number(total ?? 0)}.00\n` +
      `💵 Pago: ${pago ?? ""}` +
      (nota ? `\n📝 Nota: ${nota}` : "") +
      `\n\nEl cliente pasará a recoger. Favor de coordinar hora y ubicación.`;

    const resultados: any[] = [];

    if (GREEN_API_INSTANCE && GREEN_API_TOKEN && GREEN_API_CHAT_ID) {
      resultados.push({
        destino: "grupo",
        ...(await enviarWA(GREEN_API_CHAT_ID, mensajeGrupo))
      });
    }

    if (telefono) {
      resultados.push({
        destino: "cliente",
        ...(await enviarWA(chatIdTelefono(telefono), mensajeCliente))
      });
    }

    if (tipo_entrega === "Recoger en bodega" && vendedor_wa) {
      resultados.push({
        destino: "vendedor",
        ...(await enviarWA(chatIdTelefono(vendedor_wa), mensajeVendedor))
      });
    }

    return res.json({
      ok: true,
      resultados
    });
  } catch (error: any) {
    return res.status(500).json({
      ok: false,
      error: String(error?.message ?? error)
    });
  }
});

export default router;
