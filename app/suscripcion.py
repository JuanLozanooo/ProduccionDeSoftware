from datetime import date, timedelta

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
        self.tipo_plan = "premium"
        self.fecha_inicio = date.today()
        self.fecha_fin = date.today() + timedelta(days=30)

    def ver_estado_suscripcion(self) -> dict:
        hoy = date.today()
        activa = self.fecha_inicio <= hoy <= self.fecha_fin
        return {
            "usuario_id": self.usuario_id,
            "tipo_plan": self.tipo_plan,
            "vigente": activa,
            "inicio": str(self.fecha_inicio),
            "fin": str(self.fecha_fin)
        }
