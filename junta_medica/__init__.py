"""
Sistema multiagente de segunda opinión médica (Medicina Interna).

Arquitectura en capas (ver docs/ARQUITECTURA.md):

    config/        -> constantes y parámetros (como appsettings)
    models/       -> SOLO datos: las estructuras del sistema (como Models)
    interfaces/    -> contratos que deben cumplir las piezas intercambiables (como Services/Interfaces)
    repositories/  -> leer y guardar datos en archivos (como Persistence + Repositories)
    services/     -> la lógica del sistema (como Services/Implementation)
    factories/      -> arma y conecta los objetos (como Program.cs)
    exceptions.py -> errores propios del sistema

Cada capa se organiza por área: cases/, pharmacology/, llm/ (y más adelante knowledge/, agentes/, debate/).
"""
