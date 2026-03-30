import express from "express";
import cors from "cors";
import path from "path";
import router from "./routes/index.js";

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 👇 ESTO ES CLAVE
app.use(express.static(path.join(process.cwd(), "public")));

// API
app.use("/api", router);

// 👇 ESTO FORZA QUE / ABRA index.html
app.get("/", (req, res) => {
  res.sendFile(path.join(process.cwd(), "public", "index.html"));
});

export default app;
