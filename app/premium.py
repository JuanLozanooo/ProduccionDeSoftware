from app.usuario import Usuario


class Premium(Usuario):
    tipo_suscripcion: int

    def leer_libro_completo(self) -> None:
        pass

    def renovar_suscripcion(self) -> None:
        pass

    def cancelar_suscripcion(self) -> None:
        pass
