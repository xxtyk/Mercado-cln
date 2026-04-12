import { Router } from "express";
import pool from "../db.js";

const router = Router();

// VER PEDIDOS
router.get("/pedidos", async (_req, res) => {
  try {
    const result = await pool.query(
      "SELECT * FROM pedidos ORDER BY creado DESC"
    );

    const pedidos = result.rows.map((p) => ({
      ...p,
      productos: p.productos || []
    }));

    res.json(pedidos);
  } catch (error) {
    console.error("ERROR GET /pedidos:", error);
    res.status(500).json({ ok: false });
  }
});

// CREAR PEDIDO + ENVIAR A WHATSAPP
router.post("/pedidos", async (req, res) => {
  try {
    const pedido = {
      id: Date.now().toString(),
      ...req.body
    };

    const {
      id,
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

    await pool.query(
      `
      INSERT INTO pedidos (
        id, nombre, telefono, direccion, colonia, calle,
        vendedor, nota, entrega, subtotal, envio, total, productos
      ) VALUES (
        $1,$2,$3,$4,$5,$6,
        $7,$8,$9,$10,$11,$12,$13
      )
      `,
      [
        id,
        nombre || "",
        telefono || "",
        direccion || "",
        colonia || "",
        calle || "",
        vendedor || "",
        nota || "",
        entrega || "",
        Number(subtotal || 0),
        Number(envio || 0),
        Number(total || 0),
        JSON.stringify(productos || [])
      ]
    );

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
    console.error("ERROR POST /pedidos:", error);
    res.status(500).json({ ok: false });
  }
});

// ELIMINAR PEDIDO
router.delete("/pedidos/:id", async (req, res) => {
  try {
    await pool.query("DELETE FROM pedidos WHERE id = $1", [req.params.id]);
    res.json({ ok: true });
  } catch (error) {
    console.error("ERROR DELETE /pedidos/:id:", error);
    res.status(500).json({ ok: false });
  }
});

// MARCAR ENVIADO Y BORRAR
router.post("/pedidos/:id/whatsapp", async (req, res) => {
  try {
    await pool.query("DELETE FROM pedidos WHERE id = $1", [req.params.id]);
    res.json({ ok: true });
  } catch (error) {
    console.error("ERROR POST /pedidos/:id/whatsapp:", error);
    res.status(500).json({ ok: false });
  }
});

export default router;
