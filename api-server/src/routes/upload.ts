
import { Router } from "express";
import multer from "multer";
import ImageKit from "imagekit";

const router = Router();

const ADMIN_PASS = process.env.ADMIN_PASSWORD;

const imagekit = new ImageKit({
  publicKey: process.env.IMAGEKIT_PUBLIC_KEY || "",
  privateKey: process.env.IMAGEKIT_PRIVATE_KEY || "",
  urlEndpoint: "https://ik.imagekit.io/mercadocln"
});

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }
});

function auth(req: any, res: any): boolean {
  if (
    !ADMIN_PASS ||
    req.headers.authorization !== `Bearer ${ADMIN_PASS}`
  ) {
    res.status(401).json({
      ok: false,
      error: "No autorizado"
    });
    return false;
  }
  return true;
}

async function subirAImageKit(file: Express.Multer.File) {
  return imagekit.upload({
    file: file.buffer,
    fileName: file.originalname,
    folder: "/mercado_cln",
    useUniqueFileName: true
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

    const result = await subirAImageKit(req.file);

    return res.json({
      ok: true,
      filename: result.fileId,
      url: result.url
    });
  } catch (error) {
    console.error("ERROR UPLOAD IMAGEKIT:", error);

    return res.status(500).json({
      ok: false,
      error: "Error subiendo archivo"
    });
  }
}

router.post(
  "/upload",
  upload.single("file"),
  responderArchivo
);

router.post(
  "/admin/upload",
  upload.single("file"),
  (req, res) => {
    if (!auth(req, res)) return;
    return responderArchivo(req, res);
  }
);

export default router;
