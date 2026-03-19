import flet as ft

def main(page: ft.Page):
    page.title = "Mercado en Línea Culiacán"
    # Fondo muy oscuro como en la captura
    page.bgcolor = "#121212" 
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO

    # BARRA DE TÍTULO (HEADER)
    header = ft.Row(
        [
            # Espacio para el logo a la izquierda (reemplaza 'path_to_logo' con tu ruta)
            # ft.Image(src='path_to_logo/mercado_logo.png', height=30, width=30), 
            ft.Text("MERCADO EN LÍNEA\nCULIACÁN", size=14, weight="bold", color="white", text_align="center"),
            ft.IconButton(icon=ft.icons.SHOPPING_CART, icon_color="white", icon_size=20),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        padding=10,
    )

    # TÍTULO DE LA SECCIÓN "CATEGORÍAS"
    seccion_titulo = ft.Container(
        content=ft.Text("CATEGORÍAS", size=16, weight="bold", color="white", tracking=1),
        padding=ft.padding.symmetric(horizontal=10, vertical=15),
        bgcolor="#000000",
        width=page.width,
        alignment=ft.alignment.center,
    )

    # FUNCIÓN PARA CREAR CADA TARJETA DE CATEGORÍA
    def crear_tarjeta_categoria(nombre, color_fondo, icono=None, imagen_url=None):
        content = ft.Column(
            [
                # Contenedor superior con la imagen o icono
                ft.Container(
                    content=ft.Image(src=imagen_url, fit=ft.ImageFit.COVER) if imagen_url else ft.Icon(icono, size=50, color="white"),
                    height=130, # Altura del área de la imagen
                    alignment=ft.alignment.center,
                    border_radius=ft.border_radius.only(top_left=10, top_right=10),
                    bgcolor=color_fondo if not imagen_url else None,
                ),
                # Contenedor inferior blanco con el nombre
                ft.Container(
                    content=ft.Text(nombre, size=14, weight="bold", color="black", text_align="center"),
                    bgcolor="white",
                    padding=ft.padding.all(10),
                    alignment=ft.alignment.center,
                    border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                    height=50,
                ),
            ],
            spacing=0,
            tight=True,
        )

        return ft.Container(
            content=content,
            border_radius=10, # Bordes redondeados de la tarjeta
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color=ft.colors.with_opacity(0.3, "black")), # Sombra suave
            on_click=lambda e: print(f"Clic en {nombre}"), # Acción al hacer clic
            width=170, # Ancho fijo para mantener la cuadrícula
        )

    # DEFINICIÓN DE LAS CATEGORÍAS (COMO EN TU IMAGEN)
    # Reemplaza 'URL_DE_TU_IMAGEN_SHAMPOO' con el link real de tu imagen
    tarjeta1 = crear_tarjeta_categoria("Cuidado del cabello", "white", imagen_url="URL_DE_TU_IMAGEN_SHAMPOO")
    tarjeta2 = crear_tarjeta_categoria("Cocina", "#FF6F00", icono=ft.icons.RESTAURANT_MENU)
    tarjeta3 = crear_tarjeta_categoria("Mascotas", "#388E3C", icono=ft.icons.PETS)
    tarjeta4 = crear_tarjeta_categoria("Música y sonido", "#1E88E5", icono=ft.icons.MUSIC_NOTE_ROUNDED)
    tarjeta5 = crear_tarjeta_categoria("Belleza", "#D32F2F", icono=ft.icons.BRUSH_ROUNDED) 
    tarjeta6 = crear_tarjeta_categoria("Electrónica", "#455A64", icono=ft.icons.FLASH_ON_ROUNDED)

    # CUADRÍCULA DE CATEGORÍAS (GirdView)
    grid_categorias = ft.GridView(
        expand=True,
        runs_count=2, # Número de columnas (2 para celular)
        max_extent=180, # Ancho máximo de cada tarjeta
        child_aspect_ratio=0.8, # Relación de aspecto para tarjetas rectangulares altas
        spacing=10, # Espacio entre tarjetas
        run_spacing=10, # Espacio entre filas
        padding=10,
        controls=[tarjeta1, tarjeta2, tarjeta3, tarjeta4, tarjeta5, tarjeta6],
    )

    # AÑADIR TODO A LA PÁGINA
    page.add(
        header,
        seccion_titulo,
        grid_categorias,
    )

ft.app(target=main, assets_dir="assets")
