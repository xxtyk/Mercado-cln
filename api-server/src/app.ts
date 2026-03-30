import express from "express";
import cors from "cors";
import path from "path";
import router from "./routes/index.js";

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use(express.static(path.join(process.cwd(), "public")));

app.get("/admin", (_req, res) => {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.send(`
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Admin</title>
      <style>
        body{
          margin:0;
          font-family:Arial,sans-serif;
          background:#f5f5f5;
          color:#111;
          padding:20px;
        }
        .caja{
          background:#fff;
          padding:20px;
          border-radius:12px;
          max-width:700px;
          margin:40px auto;
          box-shadow:0 2px 10px rgba(0,0,0,0.10);
        }
        h1{
          margin-top:0;
        }
        a{
          display:inline-block;
          margin-top:14px;
          text-decoration:none;
          background:#000;
          color:#fff;
          padding:12px 16px;
          border-radius:10px;
        }
      </style>
    </head>
    <body>
      <div class="caja">
        <h1>PANEL ADMIN FUNCIONANDO</h1>
        <p>Si ves esta pantalla, la ruta /admin ya quedó bien.</p>
        <a href="/">Volver a tienda</a>
      </div>
    </body>
    </html>
  `);
});

app.use("/api", router);

app.get("*", (_req, res) => {
  res.sendFile(path.join(process.cwd(), "public", "index.html"));
});

export default app;
