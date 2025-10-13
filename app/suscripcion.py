from datetime import date

class Suscripcion:
    def __init__(self, id_suscripcion: int, usuario_id: int, tipo_plan: str, fecha_inicio: date,
                 fecha_fin: date, tarifa: int):
        self.id_suscripcion = id_suscripcion
        self.usuario_id = usuario_id
        self.tipo_plan = tipo_plan
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.tarifa = tarifa

    def activar_suscripcion_premium(self) -> None:
        pass

    def ver_estado_suscripcion(self) -> None:
        pass
