import express from "express";
import cors from "cors";
import path from "path";
import router from "./routes/index.js";

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// PUBLIC
app.use(express.static(path.join(process.cwd(), "public")));

// 🔥 ADMIN (esto te falta)
app.get("/admin", (req, res) => {
  res.sendFile(path.join(process.cwd(), "public", "admin.html"));
});

// API
app.use("/api", router);

// 🔥 FALLBACK
app.get("*", (req, res) => {
  res.sendFile(path.join(process.cwd(), "public", "index.html"));
});

export default app;
