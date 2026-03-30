import { Router } from "express";
import multer from "multer";
import fs from "fs";
import path from "path";

const router = Router();

const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "1234";
const UPLOAD_DIR = path.join(process.cwd(), "uploads");

fs.mkdirSync(UPLOAD_DIR, { recursive: true });

function auth(req: any, res: any) {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({ ok: false, error: "No autorizado" });
    return false;
  }
  return true;
}

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

router.post("/upload", upload.single("file"), (req: any, res) => {
  if (!auth(req, res)) return;

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
});

export default router;
