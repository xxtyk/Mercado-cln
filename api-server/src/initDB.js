import pool from "./db.js";

export async function initDB() {
  try {
    // ✅ TABLA PEDIDOS
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

    // 🔥 NUEVO: TABLA CATEGORÍAS
    await pool.query(`
      CREATE TABLE IF NOT EXISTS categorias (
        id TEXT PRIMARY KEY,
        slug TEXT,
        nombre TEXT,
        emoji TEXT,
        imagen TEXT
      );
    `);

    console.log("✅ DB lista completa");
  } catch (error) {
    console.error("❌ Error creando DB:", error);
  }
}
