import { Router } from "express";

const router = Router();

let pedidos: any[] = [];

// VER PEDIDOS
router.get("/pedidos", (_req, res) => {
  res.json(pedidos);
});

// CREAR PEDIDO + ENVIAR A WHATSAPP
router.post("/pedidos", async (req, res) => {
  try {
    const pedido = {
      id: Date.now().toString(),
      ...req.body
    };

    pedidos.unshift(pedido);

    const {
      nombre,
      telefono,
      direccion,
      colonia,
      calle,
      vendedor,
      nota,
      entrega,
      productos,
      subtotal,
      envio,
      total
    } = pedido;

    const textoEntrega =
      String(entrega || "").toLowerCase().includes("domicilio")
        ? "Servicio a domicilio"
        : "Recoger en bodega";

    const productosTexto = (productos || [])
      .map((p: any) => `- ${p.nombre} x${p.cantidad} = $${p.precio * p.cantidad}`)
      .join("\n");

    const direccionLineas = [
      colonia ? `Colonia: ${colonia}` : "",
      calle ? `Calle: ${calle}` : "",
      direccion ? `Dirección: ${direccion}` : ""
    ].filter(Boolean);

    const direccionFinal = direccionLineas.join("\n");

    const mensaje = `🛒 NUEVO PEDIDO

Nombre: ${nombre}
${direccionFinal}
Celular: ${telefono}
Entrega: ${textoEntrega}
Cobrar: $${total}

Producto(s):
${productosTexto}

Subtotal: $${subtotal}
Envío: $${envio}
Nota: ${nota || ""}
Vendedor: ${vendedor || ""}
`;

    const url = `${process.env.GREEN_API_HOST}/waInstance${process.env.GREEN_API_INSTANCE}/sendMessage/${process.env.GREEN_API_TOKEN}`;

    await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        chatId: process.env.GREEN_API_CHAT_ID,
        message: mensaje
      })
    });

    res.json({ ok: true, pedido });
  } catch (error) {
    console.error("ERROR WHATSAPP:", error);
    res.status(500).json({ ok: false });
  }
});

// ELIMINAR PEDIDO
router.delete("/pedidos/:id", (req, res) => {
  pedidos = pedidos.filter((p) => p.id !== req.params.id);
  res.json({ ok: true });
});

// MARCAR ENVIADO Y BORRAR
router.post("/pedidos/:id/whatsapp", (req, res) => {
  pedidos = pedidos.filter((p) => p.id !== req.params.id);
  res.json({ ok: true });
});

export default router;
