<div class="panel-control">
  <h3>Panel de Control</h3>

  <form action="/publicar" method="POST" enctype="multipart/form-data">
    <label>Nombre del Artículo:</label>
    <input type="text" name="nombre" placeholder="Ej: Shampoo Negro" required>

    <label>Precio ($):</label>
    <input type="number" name="precio" placeholder="160" step="0.01" required>

    <label>Categoría:</label>
    <select name="categoria">
      <option value="mascotas">🐶 Mascotas</option>
      <option value="cocina">🍳 Cocina</option>
      <option value="cabello">💇 Cuidado del cabello</option>
      </select>

    <div class="upload-area">
      <input type="file" name="archivo" id="archivo" required>
      <p>Toca para subir la foto o video</p>
    </div>

    <button type="submit" class="btn-publicar">PUBLICAR EN LA TIENDA</button>
  </form>
</div>
