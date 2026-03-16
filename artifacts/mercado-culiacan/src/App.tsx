import { useState, useEffect } from "react";
import Admin from "./Admin";

const BASE = import.meta.env.BASE_URL;
const COSTO_ENVIO = 40;
const PROXY_PEDIDO = "/api/webhook-pedido";

interface Vendedor {
  nombre: string;
  whatsapp: string;
}

interface Categoria {
  id: string;
  nombre: string;
  imagen: string | null;
  emoji: string;
  color: string;
}

const CATEGORIAS: Categoria[] = [
  { id: "cabello",          nombre: "Cuidado del cabello",  imagen: `${BASE}producto1.jpg`,  emoji: "💆",  color: "#7b1fa2" },
  { id: "cocina",           nombre: "Cocina",               imagen: null,                    emoji: "🍳",  color: "#e65100" },
  { id: "mascotas",         nombre: "Mascotas",             imagen: null,                    emoji: "🐾",  color: "#2e7d32" },
  { id: "musica",           nombre: "Música y sonido",      imagen: null,                    emoji: "🎵",  color: "#1565c0" },
  { id: "personal",         nombre: "Cuidado personal",     imagen: null,                    emoji: "💄",  color: "#c62828" },
  { id: "electrodomesticos",nombre: "Electrodomésticos",    imagen: null,                    emoji: "⚡",  color: "#37474f" },
];

const VENDEDORES: Vendedor[] = [
  { nombre: "Hector",   whatsapp: "526679771409" },
  { nombre: "Silvia",   whatsapp: "526674263892" },
  { nombre: "Juan",     whatsapp: "526678962503" },
  { nombre: "Brissa",   whatsapp: "526674283998" },
  { nombre: "Claudia",  whatsapp: "526671605229" },
  { nombre: "Cristian", whatsapp: "526673587278" },
  { nombre: "Amairany", whatsapp: "526677469585" },
  { nombre: "Natalia",  whatsapp: "526673513058" },
  { nombre: "Ninguno",  whatsapp: "526679771409" },
];

interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  imagen: string;
  etiqueta: string;
  precio: number;
  categoria: string;
}

const productos: Producto[] = [
  {
    id: 1,
    nombre: "Shampoo Color Rojo Vino",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto1.jpg`,
    etiqueta: "Cabello rojizo",
    precio: 120,
    categoria: "cabello",
  },
  {
    id: 2,
    nombre: "Shampoo Color Castaño Dorado",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto2.jpg`,
    etiqueta: "Cabello castaño",
    precio: 120,
    categoria: "cabello",
  },
  {
    id: 3,
    nombre: "Mascarilla Botox Keratin",
    descripcion: "Mascarilla profesional Kormesic · 1 Litro · Repara, nutre y rellena porosidad desde la primera vez",
    imagen: `${BASE}producto3.png`,
    etiqueta: "¡Oferta!",
    precio: 150,
    categoria: "cabello",
  },
];

interface ItemCarrito {
  producto: Producto;
  cantidad: number;
}

type Paso = "carrito" | "datos" | "confirmado";

function App() {
  const [carrito, setCarrito] = useState<ItemCarrito[]>([]);
  const [carritoAbierto, setCarritoAbierto] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [paso, setPaso] = useState<Paso>("carrito");
  const [nombre, setNombre] = useState("");
  const [direccion, setDireccion] = useState("");
  const [vendedor, setVendedor] = useState("");
  const [telefono, setTelefono] = useState("");
  const [nota, setNota] = useState("");
  const [tipoEntrega, setTipoEntrega] = useState<"domicilio" | "bodega" | "">("");
  const [errores, setErrores] = useState<{ nombre?: string; direccion?: string; telefono?: string; vendedor?: string; tipoEntrega?: string }>({});
  const [snapshot, setSnapshot] = useState<{ items: ItemCarrito[]; total: number; vendedorNombre: string; vendedorWA: string } | null>(null);

  const [vista, setVista] = useState<"categorias" | "productos">("categorias");
  const [categoriaActiva, setCategoriaActiva] = useState<Categoria | null>(null);
  const [adminOpen, setAdminOpen] = useState(false);
  const [productosAPI, setProductosAPI] = useState<Producto[]>([]);

  const [installPrompt, setInstallPrompt] = useState<Event | null>(null);
  const [bannerVisible, setBannerVisible] = useState(false);

  useEffect(() => {
    if (window.location.search.includes("admin")) setAdminOpen(true);
  }, []);

  useEffect(() => {
    cargarProductosAPI();
  }, []);

  function cargarProductosAPI() {
    fetch("/api/productos")
      .then(r => r.json())
      .then((data: Producto[]) => setProductosAPI(data))
      .catch(() => {});
  }

  const todosProductos = [...productosAPI, ...productos];

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e);
      setBannerVisible(true);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  const handleInstall = async () => {
    if (!installPrompt) return;
    (installPrompt as any).prompt();
    const { outcome } = await (installPrompt as any).userChoice;
    if (outcome === "accepted") setBannerVisible(false);
  };

  const mostrarToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const agregarAlCarrito = (producto: Producto) => {
    setCarrito((prev) => {
      const existente = prev.find((i) => i.producto.id === producto.id);
      if (existente) {
        return prev.map((i) =>
          i.producto.id === producto.id ? { ...i, cantidad: i.cantidad + 1 } : i
        );
      }
      return [...prev, { producto, cantidad: 1 }];
    });
    mostrarToast(`"${producto.nombre}" agregado al carrito`);
  };

  const cambiarCantidad = (id: number, delta: number) => {
    setCarrito((prev) =>
      prev
        .map((i) => i.producto.id === id ? { ...i, cantidad: i.cantidad + delta } : i)
        .filter((i) => i.cantidad > 0)
    );
  };

  const totalProductos = carrito.reduce((s, i) => s + i.producto.precio * i.cantidad, 0);
  const costoEntrega = tipoEntrega === "domicilio" ? COSTO_ENVIO : 0;
  const totalFinal = totalProductos + costoEntrega;
  const cantidadItems = carrito.reduce((s, i) => s + i.cantidad, 0);

  const validarDatos = () => {
    const e: { nombre?: string; direccion?: string; telefono?: string; vendedor?: string; tipoEntrega?: string } = {};
    if (!nombre.trim()) e.nombre = "Por favor ingresa tu nombre";
    if (!direccion.trim()) e.direccion = "Por favor ingresa tu dirección";
    if (!telefono.trim()) e.telefono = "Por favor ingresa tu número de WhatsApp";
    else if (!/^\d{10,13}$/.test(telefono.replace(/\s+/g, ""))) e.telefono = "Ingresa un número válido (10 dígitos)";
    if (!vendedor) e.vendedor = "Por favor selecciona un vendedor";
    if (!tipoEntrega) e.tipoEntrega = "Por favor selecciona cómo quieres recibir tu pedido";
    setErrores(e);
    return Object.keys(e).length === 0;
  };

  const generarMensaje = () => {
    const lineas = carrito.map(
      (i) => `  • ${i.producto.nombre} x${i.cantidad} = $${i.producto.precio * i.cantidad}.00`
    );
    return [
      "🛒 *NUEVO PEDIDO*",
      `👤 *Cliente:* ${nombre.trim()}`,
      `📱 *WhatsApp:* ${telefono.trim()}`,
      `📍 *Dirección:* ${direccion.trim()} (Culiacán, Sinaloa)`,
      `🏪 *Vendedor:* ${vendedor}`,
      "",
      "🧾 *Productos:*",
      ...lineas,
      "",
      `🚚 *Entrega:* ${tipoEntrega === "domicilio" ? `Envío a domicilio — $${COSTO_ENVIO}.00` : "Recoger en bodega — Gratis"}`,
      `💰 *TOTAL A PAGAR: $${totalFinal}.00*`,
      `💵 *Pago:* Efectivo (Contra entrega)`,
      ...(nota.trim() ? [`📝 *Nota:* ${nota.trim()}`] : []),
    ].join("\n");
  };

  const finalizarPedido = () => {
    if (!validarDatos()) return;

    const mensaje = generarMensaje();
    navigator.clipboard.writeText(mensaje).catch(() => {});

    const vendedorInfo = VENDEDORES.find(v => v.nombre === vendedor) ?? VENDEDORES[0];

    const snap = {
      items: [...carrito],
      total: totalFinal,
      vendedorNombre: vendedorInfo.nombre,
      vendedorWA: vendedorInfo.whatsapp,
    };
    setSnapshot(snap);

    const fichaWebhook = JSON.stringify({
      cliente: nombre.trim(),
      telefono: telefono.trim(),
      direccion: direccion.trim(),
      nota: nota.trim(),
      vendedor: vendedorInfo.nombre,
      vendedor_wa: vendedorInfo.whatsapp,
      tipo_entrega: tipoEntrega === "bodega" ? "Recoger en bodega" : "Envío a domicilio",
      productos: carrito.map(i => ({
        nombre: i.producto.nombre,
        cantidad: i.cantidad,
        subtotal: i.producto.precio * i.cantidad,
      })),
      total: totalFinal,
      pago: "Efectivo (Contra entrega)",
    });

    fetch(PROXY_PEDIDO, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: fichaWebhook,
    }).catch(() => {});

    if (tipoEntrega === "bodega") {
      const msgVendedor = [
        `Hola ${vendedorInfo.nombre}, acabo de hacer este pedido para recoger en bodega:`,
        "",
        ...carrito.map(i => `• ${i.producto.nombre} x${i.cantidad} = $${i.producto.precio * i.cantidad}.00`),
        "",
        `Total: $${totalFinal}.00`,
        `Pago: Efectivo (Contra entrega)`,
        `Cliente: ${nombre.trim()}`,
        `WhatsApp: https://wa.me/${telefono.trim()}`,
        "",
        "¿Me puedes dar la ubicación y decirme a qué hora paso?",
      ].join("\n");

      window.open(
        `https://wa.me/${vendedorInfo.whatsapp}?text=${encodeURIComponent(msgVendedor)}`,
        "_blank"
      );
    }

    setPaso("confirmado");
    setCarrito([]);
  };

  const abrirCarrito = () => {
    setPaso("carrito");
    setNombre("");
    setDireccion("");
    setTelefono("");
    setNota("");
    setVendedor("");
    setTipoEntrega("");
    setSnapshot(null);
    setErrores({});
    setCarritoAbierto(true);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "#f5f5f5", fontFamily: "Roboto, sans-serif" }}>

      {bannerVisible && (
        <div style={{
          backgroundColor: "#1565c0",
          color: "#fff",
          padding: "10px 16px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "10px",
          zIndex: 300,
          flexWrap: "wrap",
        }}>
          <span style={{ fontSize: "13px", fontWeight: 500, flex: 1 }}>
            📲 ¡Instala nuestra App para hacer tus pedidos más rápido!
          </span>
          <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
            <button
              onClick={handleInstall}
              style={{
                backgroundColor: "#fff",
                color: "#1565c0",
                border: "none",
                borderRadius: "20px",
                padding: "6px 16px",
                fontWeight: 700,
                fontSize: "13px",
                cursor: "pointer",
                whiteSpace: "nowrap",
              }}
            >
              Instalar
            </button>
            <button
              onClick={() => setBannerVisible(false)}
              style={{
                background: "transparent",
                border: "none",
                color: "#fff",
                fontSize: "18px",
                cursor: "pointer",
                lineHeight: 1,
                padding: "0 4px",
              }}
              aria-label="Cerrar"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <header style={{
        backgroundColor: "#000", color: "white",
        padding: "12px 20px",
        display: "flex", alignItems: "center", justifyContent: "center",
        boxShadow: "0 2px 8px rgba(0,0,0,0.5)",
        position: "sticky", top: 0, zIndex: 200,
      }}>
        <img
          src={`${BASE}logo.jpg`}
          alt="Mercado en Línea Culiacán"
          style={{ height: "72px", objectFit: "contain" }}
        />
        <button
          onClick={abrirCarrito}
          style={{
            position: "absolute", right: "16px",
            background: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.2)",
            borderRadius: "50%", width: "44px", height: "44px", cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "white", fontSize: "22px",
          }}
        >
          🛒
          {cantidadItems > 0 && (
            <span style={{
              position: "absolute", top: "2px", right: "2px",
              backgroundColor: "#f44336", color: "white", borderRadius: "50%",
              width: "18px", height: "18px", fontSize: "11px", fontWeight: 700,
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              {cantidadItems}
            </span>
          )}
        </button>
      </header>

      <main style={{ flex: 1, width: "100%", maxWidth: "600px", margin: "0 auto" }}>

        {vista === "categorias" && (
          <>
            <div style={{ backgroundColor: "#222", color: "#fff", padding: "12px 16px", textAlign: "center", letterSpacing: "2px", fontSize: "14px", fontWeight: 700 }}>
              CATEGORÍAS
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px", padding: "10px" }}>
              {CATEGORIAS.map((cat) => (
                <div
                  key={cat.id}
                  onClick={() => { setCategoriaActiva(cat); setVista("productos"); }}
                  style={{ borderRadius: "10px", overflow: "hidden", boxShadow: "0 2px 8px rgba(0,0,0,0.15)", cursor: "pointer", backgroundColor: "#fff" }}
                >
                  {cat.imagen ? (
                    <img src={cat.imagen} alt={cat.nombre} style={{ width: "100%", height: "150px", objectFit: "cover", display: "block" }} />
                  ) : (
                    <div style={{ width: "100%", height: "150px", backgroundColor: cat.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "52px" }}>
                      {cat.emoji}
                    </div>
                  )}
                  <div style={{ backgroundColor: "#fff", textAlign: "center", padding: "10px 8px", fontWeight: 700, fontSize: "14px", color: "#212121" }}>
                    {cat.nombre}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {vista === "productos" && categoriaActiva && (
          <>
            <div style={{ backgroundColor: "#222", color: "#fff", padding: "12px 16px", display: "flex", alignItems: "center", gap: "12px", letterSpacing: "1px", fontSize: "14px", fontWeight: 700 }}>
              <button
                onClick={() => setVista("categorias")}
                style={{ background: "none", border: "none", color: "#fff", fontSize: "20px", cursor: "pointer", lineHeight: 1, padding: "0 4px 0 0" }}
                aria-label="Volver"
              >
                ←
              </button>
              {categoriaActiva.nombre.toUpperCase()}
            </div>

            {(() => {
              const filtrados = todosProductos.filter(p => p.categoria === categoriaActiva.id);
              if (filtrados.length === 0) {
                return (
                  <div style={{ textAlign: "center", padding: "60px 20px", color: "#888" }}>
                    <div style={{ fontSize: "48px", marginBottom: "12px" }}>{categoriaActiva.emoji}</div>
                    <p style={{ fontSize: "16px", fontWeight: 500 }}>Próximamente productos en esta categoría</p>
                  </div>
                );
              }
              return (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "10px", padding: "10px" }}>
                  {filtrados.map((p) => (
                    <div key={p.id} style={{ backgroundColor: "white", borderRadius: "10px", boxShadow: "0 2px 8px rgba(0,0,0,0.12)", overflow: "hidden", display: "flex", flexDirection: "column" }}>
                      <div style={{ position: "relative" }}>
                        <img src={p.imagen} alt={p.nombre} style={{ width: "100%", height: "150px", objectFit: "cover", display: "block" }} />
                        <span style={{ position: "absolute", top: "8px", right: "8px", backgroundColor: "#1976d2", color: "white", padding: "3px 8px", borderRadius: "10px", fontSize: "11px", fontWeight: 600 }}>
                          {p.etiqueta}
                        </span>
                      </div>
                      <div style={{ padding: "10px", flex: 1, display: "flex", flexDirection: "column", gap: "6px" }}>
                        <h3 style={{ fontSize: "13px", fontWeight: 700, color: "#212121", margin: 0, lineHeight: 1.3 }}>{p.nombre}</h3>
                        <p style={{ fontSize: "12px", color: "#757575", margin: 0, lineHeight: "1.4", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{p.descripcion}</p>
                        <span style={{ fontSize: "17px", fontWeight: 700, color: "#1976d2" }}>${p.precio}.00</span>
                        <button
                          onClick={() => agregarAlCarrito(p)}
                          style={{ marginTop: "auto", backgroundColor: "#1976d2", color: "white", border: "none", borderRadius: "6px", padding: "8px 0", fontSize: "12px", fontWeight: 700, cursor: "pointer", letterSpacing: "0.5px" }}
                        >
                          Agregar al carrito
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              );
            })()}
          </>
        )}

      </main>

      {carritoAbierto && (
        <div
          style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.45)", zIndex: 300, display: "flex", justifyContent: "flex-end" }}
          onClick={() => setCarritoAbierto(false)}
        >
          <div
            style={{ width: "100%", maxWidth: "420px", backgroundColor: "white", height: "100%", display: "flex", flexDirection: "column", boxShadow: "-4px 0 16px rgba(0,0,0,0.2)", animation: "slideIn 0.25s ease" }}
            onClick={e => e.stopPropagation()}
          >
            <div style={{ backgroundColor: "#1976d2", color: "white", padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: "18px", fontWeight: 500 }}>
                {paso === "datos" ? "📋 Datos de entrega" : "🛒 Mi Carrito"}
              </span>
              <button onClick={() => setCarritoAbierto(false)} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer" }}>✕</button>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
              {paso === "confirmado" ? (
                <div style={{ textAlign: "center", padding: "36px 20px 100px" }}>
                  <div style={{ fontSize: "56px", marginBottom: "14px" }}>✅</div>
                  <h3 style={{ fontSize: "20px", fontWeight: 700, color: "#2e7d32", marginBottom: "10px" }}>
                    ¡Pedido recibido!
                  </h3>

                  <p style={{ fontSize: "14px", color: "#555", lineHeight: "1.7" }}>
                    {tipoEntrega === "bodega"
                      ? "¡Listo! Tu pedido ha sido recibido. Tu asesor se pondrá en contacto contigo para coordinar la entrega."
                      : "Tu pedido está confirmado. Un repartidor te contactará por WhatsApp para coordinar la entrega a tu domicilio."}
                  </p>
                </div>
              ) : paso === "datos" ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                  <p style={{ fontSize: "14px", color: "#555" }}>
                    Completa tus datos para finalizar el pedido. El resumen se enviará al grupo de WhatsApp.
                  </p>

                  <div>
                    <label style={labelStyle}>👤 Nombre completo</label>
                    <input
                      type="text"
                      placeholder="Ej: María González"
                      value={nombre}
                      onChange={e => { setNombre(e.target.value); setErrores(er => ({ ...er, nombre: undefined })); }}
                      style={{ ...inputStyle, borderColor: errores.nombre ? "#f44336" : "#e0e0e0" }}
                    />
                    {errores.nombre && <p style={errorStyle}>{errores.nombre}</p>}
                  </div>

                  <div>
                    <label style={labelStyle}>📍 Dirección de entrega (Culiacán)</label>
                    <input
                      type="text"
                      placeholder="Ej: Calle Ángel Flores 345, Col. Centro"
                      value={direccion}
                      onChange={e => { setDireccion(e.target.value); setErrores(er => ({ ...er, direccion: undefined })); }}
                      style={{ ...inputStyle, borderColor: errores.direccion ? "#f44336" : "#e0e0e0" }}
                    />
                    {errores.direccion && <p style={errorStyle}>{errores.direccion}</p>}
                  </div>

                  <div>
                    <label style={labelStyle}>📱 Número de WhatsApp</label>
                    <input
                      type="tel"
                      placeholder="Ej: 6671234567"
                      value={telefono}
                      onChange={e => { setTelefono(e.target.value.replace(/\D/g, "")); setErrores(er => ({ ...er, telefono: undefined })); }}
                      style={{ ...inputStyle, borderColor: errores.telefono ? "#f44336" : "#e0e0e0" }}
                      maxLength={13}
                    />
                    {errores.telefono && <p style={errorStyle}>{errores.telefono}</p>}
                  </div>

                  <div>
                    <label style={labelStyle}>📝 Nota (opcional)</label>
                    <textarea
                      placeholder="Ej: Dejar con el vecino, timbre no funciona, color preferido..."
                      value={nota}
                      onChange={e => setNota(e.target.value)}
                      rows={3}
                      style={{ ...inputStyle, resize: "vertical", minHeight: "70px" }}
                    />
                  </div>

                  <div>
                    <label style={labelStyle}>🧑‍💼 Nombre del vendedor</label>
                    <select
                      value={vendedor}
                      onChange={e => { setVendedor(e.target.value); setErrores(er => ({ ...er, vendedor: undefined })); }}
                      style={{ ...inputStyle, borderColor: errores.vendedor ? "#f44336" : "#e0e0e0", backgroundColor: "white", cursor: "pointer" }}
                    >
                      <option value="">— Selecciona un vendedor —</option>
                      {VENDEDORES.map(v => (
                        <option key={v.nombre} value={v.nombre}>{v.nombre}</option>
                      ))}
                    </select>
                    {errores.vendedor && <p style={errorStyle}>{errores.vendedor}</p>}
                  </div>

                  <div>
                    <label style={labelStyle}>🚚 ¿Cómo quieres recibir tu pedido?</label>
                    <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                      {[
                        { valor: "domicilio", etiqueta: "Envío a domicilio", detalle: "$40", color: "#1976d2" },
                        { valor: "bodega",    etiqueta: "Recoger en bodega", detalle: "Gratis", color: "#2e7d32" },
                      ].map(op => (
                        <button
                          key={op.valor}
                          type="button"
                          onClick={() => { setTipoEntrega(op.valor as "domicilio" | "bodega"); setErrores(er => ({ ...er, tipoEntrega: undefined })); }}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            padding: "14px 16px",
                            borderRadius: "10px",
                            border: tipoEntrega === op.valor ? `2px solid ${op.color}` : "2px solid #e0e0e0",
                            backgroundColor: tipoEntrega === op.valor ? (op.valor === "domicilio" ? "#e3f2fd" : "#e8f5e9") : "#fff",
                            cursor: "pointer",
                            textAlign: "left",
                          }}
                        >
                          <span style={{ fontSize: "15px", fontWeight: 600, color: "#212121" }}>{op.etiqueta}</span>
                          <span style={{ fontSize: "15px", fontWeight: 700, color: op.color }}>{op.detalle}</span>
                        </button>
                      ))}
                    </div>
                    {errores.tipoEntrega && <p style={errorStyle}>{errores.tipoEntrega}</p>}
                  </div>

                  <div style={{ backgroundColor: "#f9f9f9", borderRadius: "8px", padding: "14px" }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: "#333", marginBottom: "8px" }}>Resumen del pedido</p>
                    {carrito.map(i => (
                      <div key={i.producto.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#555", marginBottom: "4px" }}>
                        <span>{i.producto.nombre} x{i.cantidad}</span>
                        <span>${i.producto.precio * i.cantidad}.00</span>
                      </div>
                    ))}
                    <div style={{ borderTop: "1px solid #e0e0e0", marginTop: "8px", paddingTop: "8px", display: "flex", justifyContent: "space-between", fontSize: "13px", color: costoEntrega > 0 ? "#1976d2" : "#2e7d32" }}>
                      <span>Costo de Entrega</span>
                      <span>{costoEntrega > 0 ? `$${costoEntrega}.00` : tipoEntrega === "bodega" ? "Gratis" : "—"}</span>
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "15px", fontWeight: 700, color: "#212121", marginTop: "6px" }}>
                      <span>Total</span><span>${totalFinal}.00</span>
                    </div>
                  </div>

                  <div style={{ backgroundColor: "#e8f5e9", borderRadius: "8px", padding: "12px 14px" }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: "#2e7d32", marginBottom: "2px" }}>💵 Método de pago</p>
                    <p style={{ fontSize: "14px", color: "#333" }}>Efectivo (Contra entrega)</p>
                  </div>

                  <div style={{ backgroundColor: "#e3f2fd", borderRadius: "8px", padding: "12px 14px" }}>
                    <p style={{ fontSize: "13px", color: "#1565c0" }}>
                      ✅ Al presionar <strong>FINALIZAR</strong>, tu pedido quedará registrado y nos pondremos en contacto contigo.
                    </p>
                  </div>

                  <button
                    onClick={finalizarPedido}
                    style={{
                      display: "block",
                      width: "100%",
                      backgroundColor: "#1db510",
                      color: "#ffffff",
                      border: "none",
                      borderRadius: "16px",
                      padding: "24px 12px",
                      fontSize: "26px",
                      fontWeight: 900,
                      cursor: "pointer",
                      boxShadow: "0 0 28px rgba(29,181,16,0.6)",
                      textAlign: "center",
                      marginBottom: "120px",
                      boxSizing: "border-box",
                      letterSpacing: "1px",
                    }}
                  >
                    Finalizar
                  </button>
                </div>
              ) : carrito.length === 0 ? (
                <div style={{ textAlign: "center", padding: "60px 20px", color: "#9e9e9e" }}>
                  <div style={{ fontSize: "48px", marginBottom: "12px" }}>🛒</div>
                  <p style={{ fontSize: "15px" }}>Tu carrito está vacío</p>
                </div>
              ) : (
                <>
                  {carrito.map((item) => (
                    <div key={item.producto.id} style={{ display: "flex", alignItems: "center", gap: "12px", padding: "12px 0", borderBottom: "1px solid #f0f0f0" }}>
                      <img src={item.producto.imagen} alt={item.producto.nombre} style={{ width: "60px", height: "60px", objectFit: "cover", borderRadius: "6px" }} />
                      <div style={{ flex: 1 }}>
                        <p style={{ fontSize: "14px", fontWeight: 600, color: "#212121", marginBottom: "4px" }}>{item.producto.nombre}</p>
                        <p style={{ fontSize: "13px", color: "#1976d2", fontWeight: 600 }}>${item.producto.precio}.00</p>
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                        <button onClick={() => cambiarCantidad(item.producto.id, -1)} style={btnCantidad}>−</button>
                        <span style={{ fontWeight: 600, minWidth: "20px", textAlign: "center" }}>{item.cantidad}</span>
                        <button onClick={() => cambiarCantidad(item.producto.id, 1)} style={btnCantidad}>+</button>
                      </div>
                    </div>
                  ))}

                  <div style={{ marginTop: "20px", backgroundColor: "#f9f9f9", borderRadius: "8px", padding: "16px" }}>
                    <h4 style={{ fontSize: "15px", fontWeight: 600, color: "#333", marginBottom: "12px" }}>Resumen del pedido</h4>
                    <div style={filaResumen}><span>Subtotal</span><span>${totalProductos}.00</span></div>
                    <div style={{ ...filaResumen, color: "#1976d2" }}>
                      <span>📦 Costo de Entrega <small style={{ color: "#757575", fontSize: "11px" }}>(Solo Culiacán)</small></span>
                      <span style={{ fontWeight: 600 }}>${COSTO_ENVIO}.00</span>
                    </div>
                    <div style={{ borderTop: "1px solid #e0e0e0", marginTop: "10px", paddingTop: "10px", ...filaResumen }}>
                      <span style={{ fontWeight: 700, fontSize: "16px" }}>Total</span>
                      <span style={{ fontWeight: 700, fontSize: "16px", color: "#1976d2" }}>${totalFinal}.00</span>
                    </div>
                  </div>

                  <div style={{ marginTop: "16px", backgroundColor: "#e8f5e9", borderRadius: "8px", padding: "14px 16px" }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: "#2e7d32", marginBottom: "2px" }}>💵 Método de pago</p>
                    <p style={{ fontSize: "14px", color: "#333" }}>Efectivo (Contra entrega)</p>
                  </div>

                  <div style={{ marginTop: "12px", backgroundColor: "#fff3e0", borderRadius: "8px", padding: "12px 16px" }}>
                    <p style={{ fontSize: "13px", color: "#e65100" }}>
                      📍 Entregas únicamente en <strong>Culiacán, Sinaloa</strong>
                    </p>
                  </div>
                </>
              )}
            </div>

            {paso === "carrito" && carrito.length > 0 && (
              <div style={{ padding: "16px", borderTop: "1px solid #e0e0e0" }}>
                <button
                  onClick={() => setPaso("datos")}
                  style={btnVerde}
                  onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1b5e20"}
                  onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#2e7d32"}
                >
                  Continuar · ${totalFinal}.00
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {toast && (
        <div style={{ position: "fixed", bottom: "24px", left: "50%", transform: "translateX(-50%)", backgroundColor: "#323232", color: "white", padding: "14px 28px", borderRadius: "4px", fontSize: "14px", boxShadow: "0 4px 12px rgba(0,0,0,0.3)", zIndex: 999, animation: "fadeIn 0.3s ease", whiteSpace: "nowrap" }}>
          {toast}
        </div>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap');
        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-50%) translateY(8px); }
          to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        @keyframes slideIn {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        input:focus { outline: none; border-color: #1976d2 !important; box-shadow: 0 0 0 2px rgba(25,118,210,0.15); }
      `}</style>

      <footer style={{ textAlign: "center", padding: "16px 0 24px" }}>
        <button
          onClick={() => setAdminOpen(true)}
          style={{ background: "none", border: "none", color: "#ccc", fontSize: "11px", cursor: "pointer" }}
        >
          Admin
        </button>
      </footer>

      {adminOpen && (
        <Admin
          onClose={() => {
            setAdminOpen(false);
            cargarProductosAPI();
          }}
        />
      )}
    </div>
  );
}

const btnCantidad: React.CSSProperties = {
  width: "28px", height: "28px", borderRadius: "50%",
  border: "1px solid #1976d2", backgroundColor: "white",
  color: "#1976d2", fontSize: "16px", fontWeight: 700,
  cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center",
};

const filaResumen: React.CSSProperties = {
  display: "flex", justifyContent: "space-between",
  alignItems: "center", fontSize: "14px",
  color: "#555", marginBottom: "8px",
};

const btnVerde: React.CSSProperties = {
  width: "100%", backgroundColor: "#2e7d32",
  color: "white", border: "none", borderRadius: "4px",
  padding: "14px", fontSize: "15px", fontWeight: 600,
  cursor: "pointer", letterSpacing: "0.5px",
  transition: "background-color 0.2s",
};

const labelStyle: React.CSSProperties = {
  display: "block", fontSize: "13px", fontWeight: 600,
  color: "#555", marginBottom: "6px",
};

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "10px 12px",
  border: "1.5px solid #e0e0e0", borderRadius: "6px",
  fontSize: "14px", color: "#212121",
  transition: "border-color 0.2s",
};

const errorStyle: React.CSSProperties = {
  fontSize: "12px", color: "#f44336", marginTop: "4px",
};

export default App;
