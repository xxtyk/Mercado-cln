
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
    res.status(401).json({ ok: false });
    return false;
  }
  return true;
}

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, UPLOAD_DIR);
  },
  filename: (_req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase()
