import { Router } from "express";
import multer from "multer";
import fs from "fs";
import path from "path";

const router = Router();

const UPLOAD_DIR = path.join(process.cwd(), "uploads");

fs.mkdirSync(UPLOAD_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    const name = `${Date.now()}-${Math.random().toString(36).slice(2)}${ext}`;
    cb(null, name);
  }
});

const upload = multer({ storage });

function responderArchivo(req: any, res: any) {
  if (!req.file) {
    return res.status(400).json({
      ok: false,
      error: "No se subió archivo"
    });
  }

  return res.json({
    ok: true,
    filename: req.file.filename,
    url: `/api/uploads/${req.file.filename}`
  });
}

// Ruta simple
router.post("/upload", upload.single("file"), responderArchivo);

// Ruta que usa tu panel admin
router.post("/admin/upload", upload.single("file"), responderArchivo);

export default router;
