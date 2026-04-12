import app from "./app.js";
import { initDB } from "./initDB.js"; // 👈 NUEVO

const PORT = process.env.PORT || 3000;

// 👇 INICIALIZA BASE
initDB();

app.listen(PORT, () => {
  console.log("Servidor corriendo en puerto " + PORT);
});
