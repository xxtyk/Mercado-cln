import app from "./app";

const rawPort = process.env.PORT ?? "10000";
const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Puerto inválido: ${rawPort}`);
}

app.listen(port, "0.0.0.0", () => {
  console.log(`Servidor corriendo en puerto ${port}`);
});
