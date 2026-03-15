import { useState } from "react";

const BASE = import.meta.env.BASE_URL;

const productos = [
  {
    id: 1,
    nombre: "Shampoo Color Rojo Vino",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto1.jpg`,
    etiqueta: "Cabello rojizo",
  },
  {
    id: 2,
    nombre: "Shampoo Color Castaño Dorado",
    descripcion: "Shampoo colorante Tongrentang 4 en 1 · 500ml · Cobertura total · Actúa en 10 min",
    imagen: `${BASE}producto2.jpg`,
    etiqueta: "Cabello castaño",
  },
  {
    id: 3,
    nombre: "Mascarilla Botox Keratin",
    descripcion: "Mascarilla profesional Kormesic · 1 Litro · Repara, nutre y rellena porosidad desde la primera vez",
    imagen: `${BASE}producto3.png`,
    etiqueta: "$150",
  },
];

function App() {
  const [agregado, setAgregado] = useState<number | null>(null);

  const handleAgregar = (id: number) => {
    setAgregado(id);
    setTimeout(() => setAgregado(null), 2500);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "#f5f5f5", fontFamily: "Roboto, sans-serif" }}>
      <header style={{
        backgroundColor: "#1976d2",
        color: "white",
        padding: "0 20px",
        height: "56px",
        display: "flex",
        alignItems: "center",
        boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}>
        <span style={{ fontSize: "20px", fontWeight: 500, letterSpacing: "0.5px" }}>
          Mercado en Línea Culiacán
        </span>
      </header>

      <main style={{ flex: 1, padding: "24px 16px", maxWidth: "1100px", margin: "0 auto", width: "100%" }}>
        <h2 style={{ fontSize: "18px", fontWeight: 500, color: "#333", marginBottom: "20px" }}>
          Nuestros Productos
        </h2>

        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
          gap: "20px",
        }}>
          {productos.map((p) => (
            <div key={p.id} style={{
              backgroundColor: "white",
              borderRadius: "8px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.12)",
              overflow: "hidden",
              display: "flex",
              flexDirection: "column",
              transition: "box-shadow 0.2s",
            }}
              onMouseEnter={e => (e.currentTarget as HTMLDivElement).style.boxShadow = "0 6px 16px rgba(0,0,0,0.18)"}
              onMouseLeave={e => (e.currentTarget as HTMLDivElement).style.boxShadow = "0 2px 8px rgba(0,0,0,0.12)"}
            >
              <div style={{ position: "relative" }}>
                <img
                  src={p.imagen}
                  alt={p.nombre}
                  style={{ width: "100%", height: "280px", objectFit: "cover", display: "block" }}
                />
                <span style={{
                  position: "absolute",
                  top: "10px",
                  right: "10px",
                  backgroundColor: "#1976d2",
                  color: "white",
                  padding: "4px 10px",
                  borderRadius: "12px",
                  fontSize: "12px",
                  fontWeight: 600,
                }}>
                  {p.etiqueta}
                </span>
              </div>

              <div style={{ padding: "16px", flex: 1, display: "flex", flexDirection: "column", gap: "10px" }}>
                <h3 style={{ fontSize: "16px", fontWeight: 600, color: "#212121", margin: 0 }}>
                  {p.nombre}
                </h3>
                <p style={{ fontSize: "14px", color: "#757575", margin: 0, lineHeight: "1.5" }}>
                  {p.descripcion}
                </p>
                <button
                  onClick={() => handleAgregar(p.id)}
                  style={{
                    marginTop: "auto",
                    backgroundColor: "#1976d2",
                    color: "white",
                    border: "none",
                    borderRadius: "4px",
                    padding: "10px 0",
                    fontSize: "14px",
                    fontWeight: 500,
                    letterSpacing: "0.8px",
                    cursor: "pointer",
                    textTransform: "uppercase",
                    transition: "background-color 0.2s",
                  }}
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

      {agregado !== null && (
        <div style={{
          position: "fixed",
          bottom: "24px",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "#323232",
          color: "white",
          padding: "14px 28px",
          borderRadius: "4px",
          fontSize: "14px",
          boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
          zIndex: 999,
          animation: "fadeIn 0.3s ease",
        }}>
          ¡Producto agregado al carrito!
        </div>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600;700&display=swap');
        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-50%) translateY(8px); }
          to { opacity: 1; transform: translateX(-50%) translateY(0); }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
      `}</style>
    </div>
  );
}

export default App;
