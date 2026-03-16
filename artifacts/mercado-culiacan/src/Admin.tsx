import { useState, useRef, useEffect } from "react";

const CATEGORIAS = [
  { id: "cabello",           nombre: "Cuidado del cabello" },
  { id: "cocina",            nombre: "Cocina" },
  { id: "mascotas",          nombre: "Mascotas" },
  { id: "musica",            nombre: "Música y sonido" },
  { id: "personal",          nombre: "Cuidado personal" },
  { id: "electrodomesticos", nombre: "Electrodomésticos" },
];

const GREEN  = "#1b5e20";
const GREEN2 = "#2e7d32";
const LIGHT  = "#e8f5e9";

interface Producto {
  id: number;
  codigo: string;
  nombre: string;
  descripcion: string;
  imagen: string;
  etiqueta: string;
  precio: number;
  categoria: string;
}

interface AdminProps {
  onClose: () => void;
}

export default function Admin({ onClose }: AdminProps) {
  const [autenticado, setAutenticado] = useState(false);
  const [clave, setClave] = useState("");
  const [errorClave, setErrorClave] = useState(false);

  const [codigo,      setCodigo]      = useState("");
  const [nombre,      setNombre]      = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [categoria,   setCategoria]   = useState("");
  const [precio,      setPrecio]      = useState("");
  const [etiqueta,    setEtiqueta]    = useState("Nuevo");
  const [imagenFile,  setImagenFile]  = useState<File | null>(null);
  const [preview,     setPreview]     = useState<string>("");
  const [guardando,   setGuardando]   = useState(false);
  const [exito,       setExito]       = useState(false);
  const [errorMsg,    setErrorMsg]    = useState("");
  const [productos,   setProductos]   = useState<Producto[]>([]);
  const [tab,         setTab]         = useState<"nuevo" | "lista">("nuevo");

  const inputRef = useRef<HTMLInputElement>(null);

  const token = sessionStorage.getItem("admin_token") ?? "";

  useEffect(() => {
    if (sessionStorage.getItem("admin_ok") === "1") setAutenticado(true);
  }, []);

  useEffect(() => {
    if (autenticado) cargarProductos();
  }, [autenticado]);

  function cargarProductos() {
    fetch("/api/productos")
      .then(r => r.json())
      .then(setProductos)
      .catch(() => {});
  }

  function login() {
    sessionStorage.setItem("admin_token", clave);
    fetch("/api/admin/producto", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${clave}` },
      body: JSON.stringify({ nombre: "__test__", precio: 0, categoria: "test", descripcion: "", imagen: "", codigo: "", etiqueta: "" }),
    }).then(r => {
      if (r.status === 401) { setErrorClave(true); return; }
      sessionStorage.setItem("admin_ok", "1");
      setAutenticado(true);
    }).catch(() => setErrorClave(true));
  }

  function seleccionarImagen(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    setImagenFile(f);
    setPreview(URL.createObjectURL(f));
  }

  async function guardar() {
    if (!nombre.trim() || !categoria || !precio || !imagenFile) {
      setErrorMsg("Completa nombre, categoría, precio e imagen.");
      return;
    }
    setErrorMsg("");
    setGuardando(true);

    try {
      const tkn = sessionStorage.getItem("admin_token") ?? "";

      const form = new FormData();
      form.append("imagen", imagenFile);
      const upRes = await fetch("/api/admin/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${tkn}` },
        body: form,
      });
      const upData = await upRes.json();
      if (!upData.ok) throw new Error("Error subiendo imagen");

      const imagenUrl = `/api/uploads/${upData.filename}`;

      const res = await fetch("/api/admin/producto", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${tkn}` },
        body: JSON.stringify({ codigo, nombre, descripcion, imagen: imagenUrl, etiqueta, precio, categoria }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error("Error guardando producto");

      setExito(true);
      setTimeout(() => setExito(false), 3000);
      setCodigo(""); setNombre(""); setDescripcion(""); setCategoria("");
      setPrecio(""); setEtiqueta("Nuevo"); setImagenFile(null); setPreview("");
      cargarProductos();
    } catch (e: any) {
      setErrorMsg(e.message ?? "Error desconocido");
    } finally {
      setGuardando(false);
    }
  }

  async function eliminar(id: number) {
    if (!confirm("¿Eliminar este producto?")) return;
    const tkn = sessionStorage.getItem("admin_token") ?? "";
    await fetch(`/api/admin/producto/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${tkn}` },
    });
    cargarProductos();
  }

  const field: React.CSSProperties = {
    width: "100%", padding: "10px 12px", borderRadius: "6px",
    border: "1px solid #c8e6c9", fontSize: "14px", boxSizing: "border-box",
    outline: "none", fontFamily: "inherit",
  };
  const label: React.CSSProperties = {
    fontSize: "12px", fontWeight: 700, color: GREEN, marginBottom: "4px", display: "block", textTransform: "uppercase", letterSpacing: "0.5px",
  };

  if (!autenticado) {
    return (
      <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.7)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ backgroundColor: "white", borderRadius: "12px", padding: "36px 32px", width: "320px", boxShadow: "0 8px 32px rgba(0,0,0,0.3)", textAlign: "center" }}>
          <div style={{ fontSize: "40px", marginBottom: "8px" }}>🔒</div>
          <h2 style={{ fontSize: "18px", fontWeight: 700, color: GREEN, marginBottom: "4px" }}>Panel Admin</h2>
          <p style={{ fontSize: "13px", color: "#666", marginBottom: "20px" }}>Ingresa tu contraseña para continuar</p>
          <input
            type="password"
            placeholder="Contraseña"
            value={clave}
            onChange={e => { setClave(e.target.value); setErrorClave(false); }}
            onKeyDown={e => e.key === "Enter" && login()}
            style={{ ...field, borderColor: errorClave ? "#f44336" : "#c8e6c9", marginBottom: "8px" }}
            autoFocus
          />
          {errorClave && <p style={{ color: "#f44336", fontSize: "12px", marginBottom: "8px" }}>Contraseña incorrecta</p>}
          <button onClick={login} style={{ width: "100%", backgroundColor: GREEN, color: "white", border: "none", borderRadius: "6px", padding: "12px", fontSize: "15px", fontWeight: 700, cursor: "pointer" }}>
            Entrar
          </button>
          <button onClick={onClose} style={{ marginTop: "12px", background: "none", border: "none", color: "#999", fontSize: "13px", cursor: "pointer" }}>Cancelar</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.7)", zIndex: 1000, display: "flex", alignItems: "flex-start", justifyContent: "center", overflowY: "auto", padding: "20px 0 40px" }}>
      <div style={{ backgroundColor: "white", borderRadius: "12px", width: "100%", maxWidth: "500px", margin: "0 16px", boxShadow: "0 8px 32px rgba(0,0,0,0.3)", overflow: "hidden" }}>

        <div style={{ backgroundColor: GREEN, color: "white", padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <span style={{ fontSize: "17px", fontWeight: 700 }}>🛒 Administración de Productos</span>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer" }}>✕</button>
        </div>

        <div style={{ display: "flex", borderBottom: "2px solid #e8f5e9" }}>
          {(["nuevo", "lista"] as const).map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              flex: 1, padding: "12px", fontWeight: 700, fontSize: "13px", border: "none", cursor: "pointer",
              backgroundColor: tab === t ? LIGHT : "white",
              color: tab === t ? GREEN : "#888",
              borderBottom: tab === t ? `3px solid ${GREEN}` : "3px solid transparent",
            }}>
              {t === "nuevo" ? "➕ Nuevo Producto" : `📋 Mis Productos (${productos.length})`}
            </button>
          ))}
        </div>

        {tab === "nuevo" && (
          <div style={{ padding: "20px", display: "flex", flexDirection: "column", gap: "16px" }}>

            <div>
              <span style={label}>📷 Imagen del producto</span>
              <div
                onClick={() => inputRef.current?.click()}
                style={{
                  border: `2px dashed ${preview ? GREEN : "#c8e6c9"}`, borderRadius: "10px",
                  height: preview ? "auto" : "120px", cursor: "pointer",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  overflow: "hidden", backgroundColor: LIGHT, position: "relative",
                }}
              >
                {preview
                  ? <img src={preview} alt="preview" style={{ width: "100%", maxHeight: "200px", objectFit: "cover", display: "block" }} />
                  : <div style={{ textAlign: "center", color: "#81c784" }}>
                      <div style={{ fontSize: "36px" }}>📤</div>
                      <p style={{ fontSize: "13px", margin: "4px 0 0" }}>Toca para subir imagen (JPG / PNG)</p>
                    </div>
                }
              </div>
              <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: "none" }} onChange={seleccionarImagen} />
              {preview && <button onClick={() => { setPreview(""); setImagenFile(null); }} style={{ marginTop: "6px", background: "none", border: "none", color: "#f44336", fontSize: "12px", cursor: "pointer" }}>✕ Quitar imagen</button>}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <span style={label}>🏷️ Código / SKU</span>
                <input type="text" placeholder="Ej: SH-001" value={codigo} onChange={e => setCodigo(e.target.value)} style={field} />
              </div>
              <div>
                <span style={label}>⭐ Etiqueta</span>
                <input type="text" placeholder="Ej: Oferta, Nuevo…" value={etiqueta} onChange={e => setEtiqueta(e.target.value)} style={field} />
              </div>
            </div>

            <div>
              <span style={label}>📦 Nombre del producto</span>
              <input type="text" placeholder="Ej: Shampoo Botox 500ml" value={nombre} onChange={e => setNombre(e.target.value)} style={field} />
            </div>

            <div>
              <span style={label}>📝 Descripción</span>
              <textarea
                placeholder="Describe el producto: tamaño, beneficios, modo de uso..."
                value={descripcion}
                onChange={e => setDescripcion(e.target.value)}
                rows={4}
                style={{ ...field, resize: "vertical", minHeight: "90px" }}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
              <div>
                <span style={label}>📂 Categoría</span>
                <select value={categoria} onChange={e => setCategoria(e.target.value)} style={{ ...field, backgroundColor: "white", cursor: "pointer" }}>
                  <option value="">— Elegir —</option>
                  {CATEGORIAS.map(c => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </select>
              </div>
              <div>
                <span style={label}>💲 Precio unitario</span>
                <input type="number" min="0" placeholder="0.00" value={precio} onChange={e => setPrecio(e.target.value)} style={field} />
              </div>
            </div>

            {errorMsg && <p style={{ backgroundColor: "#fdecea", color: "#c62828", padding: "10px 12px", borderRadius: "6px", fontSize: "13px", margin: 0 }}>⚠️ {errorMsg}</p>}
            {exito    && <p style={{ backgroundColor: LIGHT,    color: GREEN2,    padding: "10px 12px", borderRadius: "6px", fontSize: "13px", margin: 0 }}>✅ Producto guardado y publicado correctamente</p>}

            <button
              onClick={guardar}
              disabled={guardando}
              style={{ backgroundColor: guardando ? "#a5d6a7" : GREEN2, color: "white", border: "none", borderRadius: "8px", padding: "14px", fontSize: "15px", fontWeight: 700, cursor: guardando ? "not-allowed" : "pointer", letterSpacing: "0.5px" }}
            >
              {guardando ? "Guardando..." : "💾 Guardar y publicar"}
            </button>
          </div>
        )}

        {tab === "lista" && (
          <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
            {productos.length === 0
              ? <p style={{ textAlign: "center", color: "#999", padding: "30px 0" }}>Aún no hay productos cargados.</p>
              : productos.map(p => (
                  <div key={p.id} style={{ display: "flex", alignItems: "center", gap: "12px", backgroundColor: LIGHT, borderRadius: "8px", padding: "10px", border: `1px solid #c8e6c9` }}>
                    <img src={p.imagen} alt={p.nombre} style={{ width: "56px", height: "56px", objectFit: "cover", borderRadius: "6px", flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{ fontWeight: 700, fontSize: "14px", color: "#212121", margin: "0 0 2px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.nombre}</p>
                      <p style={{ fontSize: "12px", color: "#555", margin: 0 }}>${p.precio}.00 · {CATEGORIAS.find(c => c.id === p.categoria)?.nombre ?? p.categoria}</p>
                    </div>
                    <button onClick={() => eliminar(p.id)} style={{ background: "none", border: "1px solid #f44336", color: "#f44336", borderRadius: "6px", padding: "6px 10px", cursor: "pointer", fontSize: "13px", flexShrink: 0 }}>🗑️</button>
                  </div>
                ))
            }
          </div>
        )}
      </div>
    </div>
  );
}
