class Usuario:
    id_usuario: int
    username: str
    email_usuario: str
    password: str
    activo: bool

    def iniciar_sesion(self) -> None:
        pass

    def cerrar_sesion(self) -> None:
        pass

    def buscar_libro(self) -> 'Libro':
        pass

    def cambiar_username(self) -> None:
        pass

    def cambiar_contraseña(self) -> None:
        pass

    def agregar_review(self) -> None:
        pass
