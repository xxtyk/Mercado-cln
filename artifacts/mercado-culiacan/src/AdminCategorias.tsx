import { useState, useEffect, useRef } from "react";

const BG      = "#1b6b3a";
const BG_DARK = "#155230";
const EMOJIS  = ["🛍️","💆","🍳","🐾","🎵","💄","⚡","🧴","👗","📱","🏠","🎮","🌿","🧹","💊"];

interface Cat {
  id: string;
  nombre: string;
  imagen: string;
  emoji: string;
  color: string;
}

interface Props { onClose: () => void; }

export default function AdminCategorias({ onClose }: Props) {
  const [autenticado, setAutenticado] = useState(false);
  const [clave, setClave]             = useState("");
  const [errorClave, setErrorClave]   = useState(false);

  const [cats,      setCats]      = useState<Cat[]>([]);
  const [modal,     setModal]     = useState<"crear" | "editar" | null>(null);
  const [editCat,   setEditCat]   = useState<Cat | null>(null);
  const [nombre,    setNombre]    = useState("");
  const [preview,   setPreview]   = useState("");
  const [imgFile,   setImgFile]   = useState<File | null>(null);
  const [guardando, setGuardando] = useState(false);
  const [errorMsg,  setErrorMsg]  = useState("");

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (sessionStorage.getItem("admin_ok") === "1") setAutenticado(true);
  }, []);
  useEffect(() => { if (autenticado) cargar(); }, [autenticado]);

  function cargar() {
    fetch("/api/categorias").then(r => r.json()).then(setCats).catch(() => {});
  }

  function login() {
    fetch("/api/admin/auth", { headers: { Authorization: `Bearer ${clave}` } })
      .then(r => {
        if (r.status === 401) { setErrorClave(true); return; }
        sessionStorage.setItem("admin_token", clave);
        sessionStorage.setItem("admin_ok", "1");
        setAutenticado(true);
      }).catch(() => setErrorClave(true));
  }

  function abrirCrear() {
    setEditCat(null); setNombre(""); setPreview(""); setImgFile(null);
    setErrorMsg(""); setModal("crear");
  }
  function abrirEditar(cat: Cat) {
    setEditCat(cat); setNombre(cat.nombre); setPreview(cat.imagen);
    setImgFile(null); setErrorMsg(""); setModal("editar");
  }
  function cerrarModal() { setModal(null); setEditCat(null); }

  function selImg(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]; if (!f) return;
    setImgFile(f); setPreview(URL.createObjectURL(f));
  }

  async function subir(): Promise<string | null> {
    if (!imgFile) return editCat?.imagen ?? "";
    const tkn  = sessionStorage.getItem("admin_token") ?? "";
    const form = new FormData();
    form.append("imagen", imgFile);
    const r    = await fetch("/api/admin/upload", { method: "POST", headers: { Authorization: `Bearer ${tkn}` }, body: form });
    const data = await r.json();
    return data.ok ? `/api/uploads/${data.filename}` : null;
  }

  async function guardarCrear() {
    if (!nombre.trim()) { setErrorMsg("Ingresa un nombre."); return; }
    setGuardando(true); setErrorMsg("");
    try {
      const tkn    = sessionStorage.getItem("admin_token") ?? "";
      const imagen = await subir();
      if (imagen === null) throw new Error("Error subiendo imagen");
      const r    = await fetch("/api/admin/categoria", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${tkn}` },
        body: JSON.stringify({ nombre, imagen, emoji: "🛍️", color: "#1976d2" }),
      });
      const d = await r.json();
      if (!d.ok) throw new Error("Error guardando");
      cargar(); cerrarModal();
    } catch (e: any) { setErrorMsg(e.message); }
    finally { setGuardando(false); }
  }

  async function guardarEditar() {
    if (!nombre.trim()) { setErrorMsg("Ingresa un nombre."); return; }
    setGuardando(true); setErrorMsg("");
    try {
      const tkn    = sessionStorage.getItem("admin_token") ?? "";
      const imagen = await subir();
      if (imagen === null) throw new Error("Error subiendo imagen");
      const r    = await fetch(`/api/admin/categoria/${editCat!.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${tkn}` },
        body: JSON.stringify({ nombre, imagen }),
      });
      const d = await r.json();
      if (!d.ok) throw new Error("Error guardando");
      cargar(); cerrarModal();
    } catch (e: any) { setErrorMsg(e.message); }
    finally { setGuardando(false); }
  }

  async function eliminar(cat: Cat) {
    if (!confirm(`¿Eliminar la categoría "${cat.nombre}"?\nTambién se eliminarán sus productos del catálogo.`)) return;
    const tkn = sessionStorage.getItem("admin_token") ?? "";
    await fetch(`/api/admin/categoria/${cat.id}`, { method: "DELETE", headers: { Authorization: `Bearer ${tkn}` } });
    cargar();
  }

  if (!autenticado) {
    return (
      <div style={{ position: "fixed", inset: 0, backgroundColor: BG, zIndex: 1000, display: "flex", flexDirection: "column" }}>
        <div style={{ backgroundColor: BG_DARK, padding: "14px 20px", display: "flex", alignItems: "center", gap: "12px" }}>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer" }}>←</button>
          <span style={{ color: "white", fontWeight: 700, fontSize: "16px", letterSpacing: "2px" }}>MIS CATÁLOGOS</span>
        </div>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "32px 24px" }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>🔒</div>
          <p style={{ color: "white", fontSize: "15px", marginBottom: "24px", opacity: 0.8 }}>Ingresa tu contraseña</p>
          <input
            type="password" value={clave} placeholder="Contraseña"
            onChange={e => { setClave(e.target.value); setErrorClave(false); }}
            onKeyDown={e => e.key === "Enter" && login()}
            style={{ background: "none", border: "none", borderBottom: "2px solid rgba(255,255,255,0.5)", color: "white", fontSize: "18px", padding: "8px 0", width: "240px", textAlign: "center", outline: "none", marginBottom: "8px" }}
            autoFocus
          />
          {errorClave && <p style={{ color: "#ffcdd2", fontSize: "13px", marginBottom: "8px" }}>Contraseña incorrecta</p>}
          <button onClick={login} style={{ marginTop: "16px", backgroundColor: "#4caf50", color: "white", border: "none", borderRadius: "4px", padding: "14px 48px", fontSize: "15px", fontWeight: 700, cursor: "pointer", letterSpacing: "1px" }}>ENTRAR</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: "fixed", inset: 0, backgroundColor: "#f5f5f5", zIndex: 1000, display: "flex", flexDirection: "column" }}>

      <div style={{ backgroundColor: BG, padding: "14px 20px", display: "flex", alignItems: "center", gap: "12px", flexShrink: 0 }}>
        <button onClick={onClose} style={{ background: "none", border: "none", color: "white", fontSize: "22px", cursor: "pointer", lineHeight: 1 }}>←</button>
        <span style={{ color: "white", fontWeight: 700, fontSize: "16px", letterSpacing: "2px", flex: 1 }}>MIS CATÁLOGOS</span>
        <span style={{ color: "white", fontSize: "22px" }}>{"<"}</span>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "0" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: "0" }}>
          {cats.map(cat => (
            <div key={cat.id} style={{ backgroundColor: "white", borderBottom: "1px solid #e0e0e0", borderRight: "1px solid #e0e0e0" }}>
              <div style={{ position: "relative" }}>
                {cat.imagen
                  ? <img src={cat.imagen} alt={cat.nombre} style={{ width: "100%", height: "160px", objectFit: "cover", display: "block" }} />
                  : <div style={{ width: "100%", height: "160px", backgroundColor: cat.color || "#1976d2", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "56px" }}>{cat.emoji}</div>
                }
                <div style={{ position: "absolute", top: "8px", right: "8px", display: "flex", flexDirection: "column", gap: "6px" }}>
                  <div style={{ width: "36px", height: "36px", borderRadius: "50%", backgroundColor: "white", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "11px", fontWeight: 700, color: "#333", boxShadow: "0 2px 6px rgba(0,0,0,0.25)", cursor: "pointer" }}>PDF</div>
                  <div style={{ width: "36px", height: "36px", borderRadius: "50%", backgroundColor: "#1565c0", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px", boxShadow: "0 2px 6px rgba(0,0,0,0.25)", cursor: "pointer" }}>{"<"}</div>
                </div>
              </div>
              <div style={{ textAlign: "center", padding: "8px 8px 4px", fontWeight: 600, fontSize: "14px", color: "#212121" }}>{cat.nombre}</div>
              <div style={{ display: "flex", gap: "6px", padding: "6px 8px 10px" }}>
                <button
                  onClick={() => eliminar(cat)}
                  style={{ flex: 1, backgroundColor: "#f44336", color: "white", border: "none", borderRadius: "4px", padding: "8px 4px", fontSize: "12px", fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" }}
                >
                  🗑️ ELIMINAR
                </button>
                <button
                  onClick={() => abrirEditar(cat)}
                  style={{ flex: 1, backgroundColor: "#f9a825", color: "white", border: "none", borderRadius: "4px", padding: "8px 4px", fontSize: "12px", fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "4px" }}
                >
                  ✏️ EDITAR
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={abrirCrear}
        style={{ position: "fixed", bottom: "24px", right: "24px", width: "56px", height: "56px", borderRadius: "50%", backgroundColor: "#4caf50", color: "white", border: "none", fontSize: "28px", fontWeight: 300, cursor: "pointer", boxShadow: "0 4px 12px rgba(0,0,0,0.3)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 10 }}
      >
        +
      </button>

      {modal && (
        <div style={{ position: "fixed", inset: 0, backgroundColor: "rgba(0,0,0,0.6)", zIndex: 2000, display: "flex", alignItems: "flex-end", justifyContent: "center" }}>
          <div style={{ backgroundColor: "white", borderRadius: "16px 16px 0 0", width: "100%", maxWidth: "480px", padding: "24px 20px 40px" }}>
            <h3 style={{ fontSize: "17px", fontWeight: 700, color: BG, marginBottom: "20px", textAlign: "center" }}>
              {modal === "crear" ? "➕ Nueva Categoría" : "✏️ Editar Categoría"}
            </h3>

            <div
              onClick={() => inputRef.current?.click()}
              style={{ width: "100%", height: "140px", border: `2px dashed ${BG}`, borderRadius: "8px", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", overflow: "hidden", marginBottom: "16px", backgroundColor: "#f1f8e9" }}
            >
              {preview
                ? <img src={preview} alt="preview" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : <div style={{ textAlign: "center", color: BG }}>
                    <div style={{ fontSize: "36px" }}>📷</div>
                    <p style={{ fontSize: "13px", margin: "6px 0 0" }}>Toca para subir foto de portada</p>
                  </div>
              }
            </div>
            <input ref={inputRef} type="file" accept="image/jpeg,image/png,image/webp" style={{ display: "none" }} onChange={selImg} />

            <label style={{ fontSize: "13px", fontWeight: 700, color: BG, display: "block", marginBottom: "6px" }}>Nombre de la categoría</label>
            <input
              type="text"
              placeholder="Ej: Ropa, Juguetes, Electrónica..."
              value={nombre}
              onChange={e => setNombre(e.target.value)}
              style={{ width: "100%", padding: "12px", border: `1.5px solid #c8e6c9`, borderRadius: "6px", fontSize: "15px", boxSizing: "border-box", outline: "none", marginBottom: "16px" }}
              autoFocus
            />

            {errorMsg && <p style={{ color: "#f44336", fontSize: "13px", marginBottom: "10px" }}>⚠️ {errorMsg}</p>}

            <div style={{ display: "flex", gap: "10px" }}>
              <button onClick={cerrarModal} style={{ flex: 1, padding: "13px", border: "1.5px solid #e0e0e0", borderRadius: "6px", backgroundColor: "white", fontSize: "14px", fontWeight: 600, cursor: "pointer", color: "#555" }}>Cancelar</button>
              <button
                onClick={modal === "crear" ? guardarCrear : guardarEditar}
                disabled={guardando}
                style={{ flex: 2, padding: "13px", border: "none", borderRadius: "6px", backgroundColor: guardando ? "#a5d6a7" : BG, color: "white", fontSize: "14px", fontWeight: 700, cursor: guardando ? "not-allowed" : "pointer", letterSpacing: "1px" }}
              >
                {guardando ? "GUARDANDO..." : "GUARDAR"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
