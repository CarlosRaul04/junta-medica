"""
Interfaz web (Streamlit). Solo muestra y recoge datos: toda la lógica está en services/ y se arma en factories/.

    main.py           -> configuración de la página, inicio de sesión y menú
    dependencies.py   -> servicios ya armados (se crean una sola vez por servidor)
    session.py        -> lo que se recuerda mientras el usuario navega (usuario, consulta abierta, borrador)
    theme.py          -> estilos visuales
    components/       -> piezas reutilizables (encabezado, alertas, diagnóstico, debate, progreso...)
    forms/            -> el formulario del caso clínico por pasos
    pages/            -> una pantalla por archivo
"""
