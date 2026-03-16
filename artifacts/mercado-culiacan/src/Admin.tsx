import { useState, useRef, useEffect, useCallback } from "react";

const CATEGORIAS = [
  { id: "cabello",           nombre: "Cuidado del cabello" },
  { id: "cocina",            nombre: "Cocina" },
  { id: "mascotas",          nombre: "Mascotas" },
  { id: "musica",            nombre: "Música y sonido" },
  { id: "personal",          nombre: "Cuidado personal" },
  { id: "electrodomesticos", nombre: "Electrodomésticos" },
];

const BG      = "#1b6b3a";
const BG_DARK = "#155230";
const BTN_G   = "#4caf50";

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

interface AdminProps { onClose: () => void; }

const underline: React.CSSProperties = {
  background: "none", border: "none", borderBottom: "1.5px solid rgba(255,255,255,0.4)",
  width: "100%", padding: "8px 0", color: "white", fontSize: "15px",
  outline: "none", fontFamily: "inherit",
};
const lbl: React.CSSProperties = {
  color: "white", fontSize: "13px", marginBottom: "4px", display: "block",
};

export default function Admin({ onClose }: AdminProps) {
  const [autenticado, setAutenticado]   = useState(false);
  const [clave, setClave]               = useState("");
  const [errorClave, setErrorClave]     = useState(false);

  const [codigo,    setCodigo]    = useState("");
  const [nombre,    setNombre]    = useState("");
  const [categoria, setCategoria] = useState("");
  const [precio,    setPrecio]    = useState("");
  const [etiqueta,  setEtiqueta]  = useState("Nuevo");
  const [imagenFile, setImagenFile] = useState<File | null>(null);
  const [preview,    setPreview]   = useState("");
  const [guardando,  setGuardando] = useState(false);
  const [exito,      setExito]     = useState(false);
  const [errorMsg,   setErrorMsg]  = useState("");
  const [productos,  setProductos] = useState<Producto[]>([]);
  const [tab, setTab]              = useState<"nuevo" | "lista">("nuevo");

  const inputRef    = useRef<HTMLInputElement>(null);
  const editorRef   = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("admin_ok") === "1") setAutenticado(true);
  }, []);
  useEffect(() => { if (autenticado) cargarProductos(); }, [autenticado]);

  function cargarProductos() {
    fetch("/api/productos").then(r => r.json()).then(setProductos).catch(() => {});
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

  const fmt = useCallback((cmd: string, val?: string) => {
    document.execCommand(cmd, false, val);
    editorRef.current?.focus();
  }, []);

  async function guardar() {
    const desc = editorRef.current?.innerHTML ?? "";
    if (!nombre.trim() || !categoria || !precio || !imagenFile) {
      setErrorMsg("Completa nombre, categoría, precio e imagen.");
      return;
    }
    setErrorMsg(""); setGuardando(true);
    try {
      const tkn = sessionStorage.getItem("admin_token") ?? "";
      const form = new FormData();
      form.append("imagen", imagenFile);
      const upRes  = await fetch("/api/admin/upload", { method: "POST", headers: { Authorization: `Bearer ${tkn}` }, body: form });
      const upData = await upRes.json();
      if (!upData.ok) throw new Error("Error subiendo imagen");

      const res  = await fetch("/api/admin/producto", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${tkn}` },
        body: JSON.stringify({ codigo, nombre, descripcion: desc, imagen: `/api/uploads/${upData.filename}`, etiqueta, precio, categoria }),
      });
      const data = await res.json();
      if (!data.ok) throw new Error("Error guardando producto");

      setExito(true); setTimeout(() => setExito(false), 3000);
      setCodigo(""); setNombre(""); setCategoria(""); setPrecio("");
      setEtiqueta("Nuevo"); setImagenFile(null); setPreview("");
      if (editorRef.current) editorRef.current.innerHTML = "";
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
    await fetch(`/api/admin/producto/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${tkn}` } });
    cargarProductos();
  }

  if (!autenticado) {
    return (
      <div style={{ position: "fixed", inset: 0, backgroundColor: BG, zIndex: 1000, display: "flex", flexDirection: "column" }}>
        <div style={{ backgroundColor: BG_DARK, padding: "16px 20px", display: "flex", alignItems: "center", gap: "12px" }}>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer", lineHeight: 1 }}>←</button>
          <span style={{ color: "white", fontWeight: 700, fontSize: "16px", letterSpacing: "1px" }}>ADMIN</span>
        </div>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px 24px" }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔒</div>
          <p style={{ color: "white", fontSize: "15px", marginBottom: "20px", opacity: 0.8 }}>Ingresa tu contraseña para continuar</p>
          <input
            type="password" placeholder="Contraseña" value={clave}
            onChange={e => { setClave(e.target.value); setErrorClave(false); }}
            onKeyDown={e => e.key === "Enter" && login()}
            style={{ ...underline, textAlign: "center", fontSize: "18px", maxWidth: "280px", marginBottom: "8px" }}
            autoFocus
          />
          {errorClave && <p style={{ color: "#ffcdd2", fontSize: "13px", marginBottom: "12px" }}>Contraseña incorrecta</p>}
          <button onClick={login} style={{ marginTop: "16px", backgroundColor: BTN_G, color: "white", border: "none", borderRadius: "4px", padding: "14px 48px", fontSize: "15px", fontWeight: 700, cursor: "pointer", letterSpacing: "1px" }}>
            ENTRAR
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: "fixed", inset: 0, backgroundColor: BG, zIndex: 1000, display: "flex", flexDirection: "column", overflowY: "auto" }}>

      <div style={{ backgroundColor: BG_DARK, padding: "14px 20px", display: "flex", alignItems: "center", gap: "12px", position: "sticky", top: 0, zIndex: 10 }}>
        <button onClick={onClose} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer", lineHeight: 1 }}>←</button>
        <span style={{ color: "white", fontWeight: 700, fontSize: "16px", letterSpacing: "2px", flex: 1 }}>PRODUCTO</span>
        <button onClick={() => setTab(tab === "nuevo" ? "lista" : "nuevo")} style={{ background: "none", border: "1px solid rgba(255,255,255,0.4)", borderRadius: "4px", color: "white", fontSize: "12px", padding: "4px 10px", cursor: "pointer" }}>
          {tab === "nuevo" ? `📋 Lista (${productos.length})` : "➕ Nuevo"}
        </button>
      </div>

      {tab === "lista" ? (
        <div style={{ padding: "16px", display: "flex", flexDirection: "column", gap: "10px" }}>
          {productos.length === 0
            ? <p style={{ color: "rgba(255,255,255,0.6)", textAlign: "center", padding: "40px 0", fontSize: "15px" }}>Aún no hay productos cargados.</p>
            : productos.map(p => (
                <div key={p.id} style={{ backgroundColor: "rgba(0,0,0,0.2)", borderRadius: "8px", padding: "12px", display: "flex", gap: "12px", alignItems: "center" }}>
                  <img src={p.imagen} alt={p.nombre} style={{ width: "60px", height: "60px", objectFit: "cover", borderRadius: "6px", flexShrink: 0 }} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ color: "white", fontWeight: 700, fontSize: "14px", margin: "0 0 3px", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.nombre}</p>
                    <p style={{ color: "rgba(255,255,255,0.7)", fontSize: "12px", margin: 0 }}>${p.precio}.00 · {CATEGORIAS.find(c => c.id === p.categoria)?.nombre ?? p.categoria}</p>
                  </div>
                  <button onClick={() => eliminar(p.id)} style={{ background: "none", border: "1px solid rgba(255,100,100,0.6)", color: "#ff8a80", borderRadius: "6px", padding: "6px 10px", cursor: "pointer", fontSize: "13px", flexShrink: 0 }}>🗑️</button>
                </div>
              ))
          }
        </div>
      ) : (
        <div style={{ padding: "0 0 100px" }}>

          <div style={{ padding: "16px 20px 8px" }}>
            <span style={{ ...lbl, fontSize: "12px", opacity: 0.85 }}>* Galería (JPG o PNG)</span>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginTop: "8px" }}>
              <div
                onClick={() => inputRef.current?.click()}
                style={{ backgroundColor: "rgba(0,0,0,0.15)", border: "1.5px solid rgba(255,255,255,0.2)", borderRadius: "6px", height: "120px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", cursor: "pointer", overflow: "hidden" }}
              >
                {preview
                  ? <img src={preview} alt="preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                  : <>
                      <svg width="52" height="44" viewBox="0 0 52 44" fill="none">
                        <path d="M20 8H32L36 14H44C46.2 14 48 15.8 48 18V38C48 40.2 46.2 42 44 42H8C5.8 42 4 40.2 4 38V18C4 15.8 5.8 14 8 14H16L20 8Z" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5" fill="none"/>
                        <circle cx="26" cy="28" r="8" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5" fill="none"/>
                        <path d="M38 20L38 20" stroke="rgba(255,255,255,0.7)" strokeWidth="2" strokeLinecap="round"/>
                        <circle cx="42" cy="20" r="3" fill="#4caf50"/>
                        <path d="M41 20H43M42 19V21" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                      <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "11px", marginTop: "6px" }}>Foto</span>
                    </>
                }
              </div>
              <div style={{ backgroundColor: "rgba(0,0,0,0.15)", border: "1.5px solid rgba(255,255,255,0.2)", borderRadius: "6px", height: "120px", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", opacity: 0.5 }}>
                <svg width="54" height="40" viewBox="0 0 54 40" fill="none">
                  <rect x="2" y="6" width="34" height="28" rx="3" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5" fill="none"/>
                  <path d="M36 14L50 7V33L36 26V14Z" stroke="rgba(255,255,255,0.7)" strokeWidth="2.5" fill="none"/>
                  <circle cx="40" cy="8" r="3" fill="#4caf50"/>
                  <path d="M39 8H41M40 7V9" stroke="white" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "11px", marginTop: "6px" }}>Video (próx.)</span>
              </div>
            </div>
            <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: "none" }} onChange={seleccionarImagen} />
            {preview && <button onClick={() => { setPreview(""); setImagenFile(null); }} style={{ marginTop: "6px", background: "none", border: "none", color: "rgba(255,150,150,0.9)", fontSize: "12px", cursor: "pointer", padding: 0 }}>✕ Quitar imagen</button>}
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-between" }}>
              <div style={{ flex: 1 }}>
                <span style={lbl}>* Codigo (Ingresa manualmente o usa el lector)</span>
                <input type="text" placeholder="Ej. 001" value={codigo} onChange={e => setCodigo(e.target.value)} style={{ ...underline, color: "rgba(255,255,255,0.5)" }} />
              </div>
              <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "22px", paddingBottom: "8px", marginLeft: "12px" }}>⬜</span>
            </div>
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <span style={lbl}>* Nombre</span>
            <input type="text" placeholder="" value={nombre} onChange={e => setNombre(e.target.value)} style={underline} />
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <span style={lbl}>* Descripción</span>
            <div style={{ backgroundColor: "white", borderRadius: "6px", marginTop: "8px", overflow: "hidden" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "2px", padding: "6px 8px", borderBottom: "1px solid #e0e0e0", flexWrap: "wrap" }}>
                <select defaultValue="Normal" style={{ border: "none", fontSize: "13px", color: "#333", cursor: "pointer", outline: "none", marginRight: "4px", background: "transparent" }}>
                  <option>Normal</option><option>Título</option><option>Subtítulo</option>
                </select>
                {[
                  { label: "A",  title: "Color",         action: () => {} },
                  { label: "B",  title: "Negrita",       action: () => fmt("bold") },
                  { label: "I",  title: "Cursiva",       action: () => fmt("italic") },
                  { label: "≡",  title: "Lista ordenada",    action: () => fmt("insertOrderedList") },
                  { label: "☰",  title: "Lista desordenada", action: () => fmt("insertUnorderedList") },
                ].map(btn => (
                  <button key={btn.label} title={btn.title} onMouseDown={e => { e.preventDefault(); btn.action(); }}
                    style={{ background: "none", border: "none", padding: "4px 7px", borderRadius: "4px", cursor: "pointer", fontSize: btn.label === "B" ? "15px" : "14px", fontWeight: btn.label === "B" ? 900 : btn.label === "I" ? 400 : 600, fontStyle: btn.label === "I" ? "italic" : "normal", color: "#333" }}>
                    {btn.label}
                  </button>
                ))}
              </div>
              <div
                ref={editorRef}
                contentEditable
                suppressContentEditableWarning
                data-placeholder="Inserta el texto aquí"
                style={{ minHeight: "80px", padding: "10px 12px", fontSize: "14px", color: "#333", outline: "none" }}
              />
            </div>
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <span style={lbl}>Catálogo / Categoría</span>
            <select value={categoria} onChange={e => setCategoria(e.target.value)}
              style={{ ...underline, cursor: "pointer" }}>
              <option value="" style={{ backgroundColor: BG }}>— Elegir categoría —</option>
              {CATEGORIAS.map(c => <option key={c.id} value={c.id} style={{ backgroundColor: BG }}>{c.nombre}</option>)}
            </select>
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <span style={lbl}>* Precio Unitario</span>
            <input type="number" min="0" placeholder="" value={precio} onChange={e => setPrecio(e.target.value)} style={underline} />
          </div>

          <div style={{ padding: "14px 20px", borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            <span style={lbl}>Etiqueta (ej: Oferta, Nuevo…)</span>
            <input type="text" placeholder="Nuevo" value={etiqueta} onChange={e => setEtiqueta(e.target.value)} style={underline} />
          </div>

          <div style={{ padding: "14px 20px", display: "flex", alignItems: "center", gap: "12px", backgroundColor: "rgba(0,0,0,0.1)" }}>
            <input type="checkbox" id="avanzadas" style={{ width: "18px", height: "18px", cursor: "pointer", accentColor: BTN_G }} />
            <label htmlFor="avanzadas" style={{ color: BTN_G, fontSize: "13px", fontWeight: 700, letterSpacing: "0.5px", cursor: "pointer" }}>
              OPCIONES AVANZADAS (Promos, Tallas, Colores, etc.)
            </label>
          </div>

          {errorMsg && <div style={{ margin: "0 20px", padding: "10px 14px", backgroundColor: "rgba(244,67,54,0.2)", borderRadius: "6px", color: "#ffcdd2", fontSize: "13px" }}>⚠️ {errorMsg}</div>}
          {exito    && <div style={{ margin: "0 20px", padding: "10px 14px", backgroundColor: "rgba(76,175,80,0.25)", borderRadius: "6px", color: "#c8e6c9", fontSize: "13px" }}>✅ Producto guardado y publicado</div>}

          <div style={{ position: "fixed", bottom: 0, left: 0, right: 0, padding: "12px 20px", backgroundColor: BG_DARK, zIndex: 20 }}>
            <button
              onClick={guardar}
              disabled={guardando}
              style={{ width: "100%", backgroundColor: guardando ? "#388e3c" : BTN_G, color: "white", border: "none", borderRadius: "4px", padding: "16px", fontSize: "15px", fontWeight: 700, cursor: guardando ? "not-allowed" : "pointer", letterSpacing: "2px" }}
            >
              {guardando ? "GUARDANDO..." : "GUARDAR"}
            </button>
          </div>

        </div>
      )}
    </div>
  );
}
