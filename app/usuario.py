from typing import Optional
from app.libro import Libro

class Usuario:
    def __init__(self, id_usuario: int, username: str, email_usuario: str, password: str, activo: bool = True):
        self.id_usuario = id_usuario
        self.username = username
        self.email_usuario = email_usuario
        self.password = password
        self.activo = activo

    def iniciar_sesion(self) -> None:
        pass

    def cerrar_sesion(self) -> None:
        pass

    def buscar_libro(self) -> Optional[Libro]:
        pass

    def cambiar_username(self, nuevo_username: str) -> None:
        self.username = nuevo_username

    def cambiar_contrasena(self, nueva_contrasena: str) -> None:
        self.password = nueva_contrasena