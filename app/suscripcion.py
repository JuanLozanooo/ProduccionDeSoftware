from datetime import date

class Suscripcion:
    id_suscripcion: int
    usuario_id: int
    tipo_plan: str
    fecha_inicio: date
    fecha_fin: date
    tarifa: int

    def activar_suscripcion_premium(self) -> None:
        pass

    def ver_estado_suscripcion(self) -> None:
        pass
