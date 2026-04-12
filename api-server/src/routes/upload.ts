import { Router } from "express";
import multer from "multer";
import cloudinary from "cloudinary";

const router = Router();
const ADMIN_PASS = process.env.ADMIN_PASSWORD ?? "mercado2024";

cloudinary.v2.config({
  cloud_name: process.env.CLOUDINARY_CLOUD_NAME,
  api_key: process.env.CLOUDINARY_API_KEY,
  api_secret: process.env.CLOUDINARY_API_SECRET
});

const upload = multer({ storage: multer.memoryStorage() });

function auth(req: any, res: any): boolean {
  if (req.headers.authorization !== `Bearer ${ADMIN_PASS}`) {
    res.status(401).json({
      ok: false,
      error: "No autorizado"
    });
    return false;
  }
  return true;
}

async function subirACloudinary(file: Express.Multer.File) {
  return await new Promise<any>((resolve, reject) => {
    const stream = cloudinary.v2.uploader.upload_stream(
      {
        folder: "mercado_cln"
      },
      (error, result) => {
        if (error) reject(error);
        else resolve(result);
      }
    );

    stream.end(file.buffer);
  });
}

async function responderArchivo(req: any, res: any) {
  try {
    if (!req.file) {
      return res.status(400).json({
        ok: false,
        error: "No se subió archivo"
      });
    }

    const result = await subirACloudinary(req.file);

    return res.json({
      ok: true,
      filename: result.public_id,
      url: result.secure_url
    });
  } catch (error) {
    console.error("ERROR UPLOAD CLOUDINARY:", error);
    return res.status(500).json({
      ok: false,
      error: "Error subiendo archivo"
    });
  }
}

// Ruta simple
router.post("/upload", upload.single("file"), responderArchivo);

// Ruta que usa tu panel admin
router.post("/admin/upload", upload.single("file"), (req, res) => {
  if (!auth(req, res)) return;
  return responderArchivo(req, res);
});

export default router;
