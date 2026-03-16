import { Router } from "express";
import multer from "multer";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";
const UPLOAD_DIR = path.join(__dirname, "../../uploads");

const storage = multer.diskStorage({
  destination: UPLOAD_DIR,
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, `producto_${Date.now()}${ext}`);
  },
});

const upload = multer({
  storage,
  fileFilter: (_req, file, cb) => {
    const ok = ["image/jpeg", "image/png", "image/webp"].includes(file.mimetype);
    cb(null, ok);
  },
  limits: { fileSize: 8 * 1024 * 1024 },
});

const router = Router();

router.post("/admin/upload", (req: any, res: any) => {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    return res.status(401).json({ ok: false, error: "No autorizado" });
  }
  upload.single("imagen")(req, res, (err) => {
    if (err || !req.file) {
      return res.status(400).json({ ok: false, error: "Error al subir imagen" });
    }
    res.json({ ok: true, filename: req.file.filename });
  });
});

export default router;
