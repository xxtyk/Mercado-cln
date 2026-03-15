import { useState } from "react";

function App() {
  const [mensaje, setMensaje] = useState<string | null>(null);

  const handleClick = () => {
    setMensaje("¡Bienvenido al Mercado en Línea Culiacán!");
    setTimeout(() => setMensaje(null), 3000);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", backgroundColor: "#f5f5f5", fontFamily: "Roboto, sans-serif" }}>
      <header style={{
        backgroundColor: "#1976d2",
        color: "white",
        padding: "0 16px",
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

      <main style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: "24px",
        padding: "32px 16px",
      }}>
        <button
          onClick={handleClick}
          style={{
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            borderRadius: "4px",
            padding: "12px 32px",
            fontSize: "16px",
            fontWeight: 500,
            letterSpacing: "1px",
            cursor: "pointer",
            boxShadow: "0 3px 6px rgba(0,0,0,0.2)",
            textTransform: "uppercase",
            transition: "background-color 0.2s, box-shadow 0.2s",
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1565c0";
            (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 6px 12px rgba(0,0,0,0.25)";
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLButtonElement).style.backgroundColor = "#1976d2";
            (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 3px 6px rgba(0,0,0,0.2)";
          }}
        >
          Explorar Productos
        </button>

        {mensaje && (
          <div style={{
            backgroundColor: "#323232",
            color: "white",
            padding: "14px 24px",
            borderRadius: "4px",
            fontSize: "14px",
            boxShadow: "0 3px 8px rgba(0,0,0,0.3)",
            animation: "fadeIn 0.3s ease",
          }}>
            {mensaje}
          </div>
        )}
      </main>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
      `}</style>
    </div>
  );
}

export default App;
