import { useState } from "react";

const BASE = import.meta.env.BASE_URL;
const COSTO_ENVIO = 40;
const VENDEDOR = "Mercado en Línea Culiacán";
const GRUPO_WA = "https://chat.whatsapp.com/HtBWXyZmMAxJImgPY5SRXU";

interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  imagen: string;
  etiqueta: string;
  precio: number;
}

const productos: Producto[] = [
  {
    id: 1,
    nombre: "Shampoo Color Rojo Vino",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto1.jpg`,
    etiqueta: "Cabello rojizo",
    precio: 120,
  },
  {
    id: 2,
    nombre: "Shampoo Color Castaño Dorado",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto2.jpg`,
    etiqueta: "Cabello castaño",
    precio: 120,
  },
  {
    id: 3,
    nombre: "Mascarilla Botox Keratin",
    descripcion: "Mascarilla profesional Kormesic · 1 Litro · Repara, nutre y rellena porosidad desde la primera vez",
    imagen: `${BASE}producto3.png`,
    etiqueta: "¡Oferta!",
    precio: 150,
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
  const [errores, setErrores] = useState<{ nombre?: string; direccion?: string }>({});

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
  const totalFinal = totalProductos + (carrito.length > 0 ? COSTO_ENVIO : 0);
  const cantidadItems = carrito.reduce((s, i) => s + i.cantidad, 0);

  const validarDatos = () => {
    const e: { nombre?: string; direccion?: string } = {};
    if (!nombre.trim()) e.nombre = "Por favor ingresa tu nombre";
    if (!direccion.trim()) e.direccion = "Por favor ingresa tu dirección";
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
      `📍 *Dirección:* ${direccion.trim()} (Culiacán, Sinaloa)`,
      `🏪 *Vendedor:* ${VENDEDOR}`,
      "",
      "🧾 *Productos:*",
      ...lineas,
      "",
      `📦 *Costo de entrega:* $${COSTO_ENVIO}.00 (Solo Culiacán)`,
      `💰 *TOTAL A PAGAR: $${totalFinal}.00*`,
      `💵 *Pago:* Efectivo (Contra entrega)`,
    ].join("\n");
  };

  const finalizarPedido = () => {
    if (!validarDatos()) return;

    const mensaje = generarMensaje();

    navigator.clipboard.writeText(mensaje).catch(() => {});

    window.open(GRUPO_WA, "_blank");

    setPaso("confirmado");
    setCarrito([]);
  };

  const abrirCarrito = () => {
    setPaso("carrito");
    setNombre("");
    setDireccion("");
    setErrores({});
    setCarritoAbierto(true);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "#f5f5f5", fontFamily: "Roboto, sans-serif" }}>
      <header style={{
        backgroundColor: "#1976d2", color: "white",
        padding: "0 20px", height: "56px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        boxShadow: "0 2px 4px rgba(0,0,0,0.3)", position: "sticky", top: 0, zIndex: 200,
      }}>
        <span style={{ fontSize: "20px", fontWeight: 500, letterSpacing: "0.5px" }}>
          Mercado en Línea Culiacán
        </span>
        <button
          onClick={abrirCarrito}
          style={{
            background: "rgba(255,255,255,0.15)", border: "none", borderRadius: "50%",
            width: "44px", height: "44px", cursor: "pointer",
            display: "flex", alignItems: "center", justifyContent: "center",
            position: "relative", color: "white", fontSize: "22px",
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

      <main style={{ flex: 1, padding: "24px 16px", maxWidth: "1100px", margin: "0 auto", width: "100%" }}>
        <h2 style={{ fontSize: "18px", fontWeight: 500, color: "#333", marginBottom: "20px" }}>Nuestros Productos</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "20px" }}>
          {productos.map((p) => (
            <div key={p.id}
              style={{ backgroundColor: "white", borderRadius: "8px", boxShadow: "0 2px 8px rgba(0,0,0,0.12)", overflow: "hidden", display: "flex", flexDirection: "column", transition: "box-shadow 0.2s" }}
              onMouseEnter={e => (e.currentTarget as HTMLDivElement).style.boxShadow = "0 6px 16px rgba(0,0,0,0.18)"}
              onMouseLeave={e => (e.currentTarget as HTMLDivElement).style.boxShadow = "0 2px 8px rgba(0,0,0,0.12)"}
            >
              <div style={{ position: "relative" }}>
                <img src={p.imagen} alt={p.nombre} style={{ width: "100%", height: "280px", objectFit: "cover", display: "block" }} />
                <span style={{ position: "absolute", top: "10px", right: "10px", backgroundColor: "#1976d2", color: "white", padding: "4px 10px", borderRadius: "12px", fontSize: "12px", fontWeight: 600 }}>
                  {p.etiqueta}
                </span>
              </div>
              <div style={{ padding: "16px", flex: 1, display: "flex", flexDirection: "column", gap: "10px" }}>
                <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#212121", margin: 0 }}>{p.nombre}</h3>
                <p style={{ fontSize: "14px", color: "#757575", margin: 0, lineHeight: "1.5" }}>{p.descripcion}</p>
                <span style={{ fontSize: "20px", fontWeight: 700, color: "#1976d2" }}>${p.precio}.00</span>
                <button
                  onClick={() => agregarAlCarrito(p)}
                  style={{ marginTop: "auto", backgroundColor: "#1976d2", color: "white", border: "none", borderRadius: "4px", padding: "10px 0", fontSize: "14px", fontWeight: 500, letterSpacing: "0.8px", cursor: "pointer", textTransform: "uppercase", transition: "background-color 0.2s" }}
                  onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1565c0"}
                  onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1976d2"}
                >
                  Agregar al carrito
                </button>
              </div>
            </div>
          ))}
        </div>
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
                <div style={{ textAlign: "center", padding: "40px 20px" }}>
                  <div style={{ fontSize: "52px", marginBottom: "16px" }}>✅</div>
                  <h3 style={{ fontSize: "18px", fontWeight: 600, color: "#2e7d32", marginBottom: "12px" }}>
                    ¡Gracias por su compra!
                  </h3>
                  <p style={{ fontSize: "14px", color: "#555", lineHeight: "1.6", marginBottom: "16px" }}>
                    Un repartidor le mandará WhatsApp para la entrega.
                  </p>
                  <div style={{ backgroundColor: "#e8f5e9", borderRadius: "8px", padding: "14px", fontSize: "13px", color: "#2e7d32" }}>
                    📋 El resumen del pedido fue copiado automáticamente. Pégalo en el grupo de WhatsApp si aún no se envió.
                  </div>
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

                  <div style={{ backgroundColor: "#f9f9f9", borderRadius: "8px", padding: "14px" }}>
                    <p style={{ fontSize: "13px", fontWeight: 600, color: "#333", marginBottom: "8px" }}>Resumen del pedido</p>
                    {carrito.map(i => (
                      <div key={i.producto.id} style={{ display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#555", marginBottom: "4px" }}>
                        <span>{i.producto.nombre} x{i.cantidad}</span>
                        <span>${i.producto.precio * i.cantidad}.00</span>
                      </div>
                    ))}
                    <div style={{ borderTop: "1px solid #e0e0e0", marginTop: "8px", paddingTop: "8px", display: "flex", justifyContent: "space-between", fontSize: "13px", color: "#1976d2" }}>
                      <span>Costo de Entrega</span><span>$40.00</span>
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
                      💬 Al presionar <strong>FINALIZAR</strong>, se abrirá el grupo de WhatsApp con el pedido listo para enviar.
                    </p>
                  </div>
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

            <div style={{ padding: "16px", borderTop: "1px solid #e0e0e0" }}>
              {paso === "carrito" && carrito.length > 0 && (
                <button
                  onClick={() => setPaso("datos")}
                  style={btnVerde}
                  onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1b5e20"}
                  onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#2e7d32"}
                >
                  Continuar · ${totalFinal}.00
                </button>
              )}
              {paso === "datos" && (
                <div style={{ display: "flex", gap: "10px" }}>
                  <button
                    onClick={() => setPaso("carrito")}
                    style={{ ...btnVerde, backgroundColor: "#757575", flex: "0 0 auto", padding: "14px 18px", fontSize: "13px" }}
                    onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#616161"}
                    onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#757575"}
                  >
                    ← Volver
                  </button>
                  <button
                    onClick={finalizarPedido}
                    style={{ ...btnVerde, flex: 1 }}
                    onMouseEnter={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1b5e20"}
                    onMouseLeave={e => (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#2e7d32"}
                  >
                    ✅ FINALIZAR · ${totalFinal}.00
                  </button>
                </div>
              )}
            </div>
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
