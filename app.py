@app.route("/guardar_configuracion", methods=["POST"])
def guardar_configuracion():
    usuario = request.form.get("usuario", "")
    notificaciones = request.form.get("notificaciones") == "on"
    logo_file = request.files.get("logo")

    config_data = {
        "usuario": usuario,
        "notificaciones": notificaciones
    }

    # Subir logo a Cloudinary si se seleccionó un archivo
    if logo_file and logo_file.filename != "":
        upload_result = cloudinary.uploader.upload(logo_file)
        config_data["logo"] = upload_result.get("secure_url")
    else:
        # Mantener el logo actual si ya existía
        config_actual = cargar_json(CONFIG_FILE)
        if config_actual.get("logo"):
            config_data["logo"] = config_actual["logo"]

    guardar_json(CONFIG_FILE, config_data)
    flash("Configuración guardada correctamente")
    return redirect(url_for("configuracion"))
