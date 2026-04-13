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

    await pool.query(`
      CREATE TABLE IF NOT EXISTS categorias (
        id TEXT PRIMARY KEY,
        slug TEXT,
        nombre TEXT,
        emoji TEXT,
        imagen TEXT
      );
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        codigo TEXT,
        nombre TEXT,
        descripcion TEXT,
        imagen TEXT,
        etiqueta TEXT,
        precio NUMERIC DEFAULT 0,
        categoria TEXT,
        categoria_id TEXT
      );
    `);

    await pool.query(`
      CREATE TABLE IF NOT EXISTS vendedores (
        id SERIAL PRIMARY KEY,
        nombre TEXT UNIQUE
      );
    `);

    console.log("✅ DB lista completa");
  } catch (error) {
    console.error("❌ Error creando DB:", error);
  }
}
