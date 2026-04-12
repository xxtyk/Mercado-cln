
import pool from "./db.js";

export async function initDB() {
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
      subtotal NUMERIC,
      envio NUMERIC,
      total NUMERIC,
      productos JSONB,
      creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `);

  console.log("✅ DB lista");
}
