import pool from "./db.js";

export async function initDB() {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS pedidos (
        id TEXT PRIMARY KEY,
        nombre TEXT,
        telefono TEXT,
        direccion TEXT,
        colonia TEXT,
        calle TEXT,
        vendedor TEXT,
        nota TEXT,
        entrega TEXT,
        subtotal NUMERIC DEFAULT 0,
        envio NUMERIC DEFAULT 0,
        total NUMERIC DEFAULT 0,
        productos JSONB DEFAULT '[]',
        creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
      );
    `);

    console.log("✅ DB lista");
  } catch (error) {
    console.error("❌ Error creando DB:", error);
  }
}
