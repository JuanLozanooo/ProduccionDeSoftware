from app.usuario import Usuario

class UsuarioPago(Usuario):
    def __init__(self, id_usuario: int, username: str, email_usuario: str, password: str,
                 tipo_suscripcion: int, activo: bool = True):
        super().__init__(id_usuario, username, email_usuario, password, activo)
        self.tipo_suscripcion = tipo_suscripcion

    def leer_libro_completo(self) -> None:
        pass

    def renovar_suscripcion(self) -> None:
        pass

    def cancelar_suscripcion(self) -> None:
        pass