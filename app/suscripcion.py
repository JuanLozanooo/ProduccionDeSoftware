from datetime import date
from typing import TYPE_CHECKING, Dict, Any, Union
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

if TYPE_CHECKING:
    from app.usuario import Usuario

class Suscripcion:
    def __init__(self, id_suscripcion: int, usuario_id: int, mes_inicio: int,
                 mes_fin: int, tarifa: int):
        self.id_suscripcion = id_suscripcion
        self.usuario_id = usuario_id
        self.mes_inicio = mes_inicio
        self.mes_fin = mes_fin
        self.tarifa = tarifa

    @staticmethod
    async def activar_suscripcion_premium(session: AsyncSession, usuario: "Usuario", codigo: str) -> str:
        if not codigo.isdigit() or len(codigo) != 5:
            return "Código inválido. Debe ser un código numérico de 5 dígitos."

        last_digit = int(codigo[-1])
        if last_digit not in [1, 2, 3]:
            return "Código inválido. El último dígito es incorrecto."

        duracion_map = {1: 1, 2: 3, 3: 6}
        duracion_meses = duracion_map[last_digit]
        tarifa = last_digit
        
        current_month = date.today().month
        mes_fin_calculado = (current_month + duracion_meses - 1) % 12 + 1

        update_user_query = text(
            "UPDATE usuario SET rol = :rol, mes_suscripcion = :mes WHERE id_usuario = :uid"
        )
        user_params = {"rol": 2, "mes": current_month, "uid": usuario.id_usuario}

        insert_sub_query = text(
            "INSERT INTO suscripcion (usuario_id, mes_inicio, mes_fin, tarifa) "
            "VALUES (:uid, :inicio, :fin, :tarifa)"
        )
        sub_params = {
            "uid": usuario.id_usuario,
            "inicio": current_month,
            "fin": mes_fin_calculado,
            "tarifa": tarifa
        }

        try:
            await session.execute(update_user_query, user_params)
            await session.execute(insert_sub_query, sub_params)
            await session.commit()
            
            usuario.rol = 2
            usuario.mes_suscripcion = current_month
            return f"Suscripción Premium activada por {duracion_meses} meses."
        except Exception as e:
            await session.rollback()
            return f"Error al activar la suscripción: {e}"

    @staticmethod
    async def ver_estado_suscripcion(session: AsyncSession, usuario: "Usuario") -> Union[Dict[str, Any], str]:
        if usuario.rol == 0:
            return {
                "usuario_id": usuario.id_usuario,
                "tarifa": "Vitalicia",
                "vigente": True,
                "mes_inicio": "00",
                "mes_fin": "00"
            }
        
        if usuario.rol == 1:
            return "No tienes una suscripción activa, pásate a Premium."

        if usuario.rol == 2:
            query = text(
                "SELECT mes_inicio, mes_fin, tarifa FROM suscripcion "
                "WHERE usuario_id = :uid ORDER BY id_suscripcion DESC LIMIT 1"
            )
            result = await session.execute(query, {"uid": usuario.id_usuario})
            sub_data = result.fetchone()

            if not sub_data:
                return "Error: Usuario Premium sin registro de suscripción."

            mes_inicio, mes_fin, tarifa = sub_data
            mes_actual = date.today().month
            activa = False

            if mes_inicio <= mes_fin:
                activa = mes_inicio <= mes_actual <= mes_fin
            else: # Handles year wrap-around
                activa = (mes_actual >= mes_inicio) or (mes_actual <= mes_fin)

            return {
                "usuario_id": usuario.id_usuario,
                "tarifa": tarifa,
                "vigente": activa,
                "mes_inicio": mes_inicio,
                "mes_fin": mes_fin
            }
        
        return "Rol de usuario no reconocido."