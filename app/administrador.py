from typing import Optional
from app.libro import Libro
from app.usuario import Usuario

class Administrador:
    def __init__(self, id_admin: int, username: str, email: str, password: str):
        self.id_admin = id_admin
        self.username = username
        self.email = email
        self.password = password

    # Métodos CRUD para Usuario
    def crear_usuario(self) -> Usuario:
        pass

    def consultar_usuario(self, id_usuario: int) -> Optional[Usuario]:
        pass

    def actualizar_usuario(self, id_usuario: int) -> None:
        pass

    def eliminar_usuario(self, id_usuario: int) -> None:
        pass

    def gestionar_estado_usuario(self, usuario: Usuario) -> None:
        pass

    # Métodos CRUD para Libro
    def crear_libro(self) -> Libro:
        pass

    def consultar_libro(self, id_libro: int) -> Optional[Libro]:
        pass

    def actualizar_libro(self, id_libro: int) -> None:
        pass

    def eliminar_libro(self, id_libro: int) -> None:
        pass