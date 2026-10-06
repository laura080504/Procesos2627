class PermisoInsuficiente(Exception):
    def __init__(self):
        super().__init__("No tienes permiso para realizar esta acción")
