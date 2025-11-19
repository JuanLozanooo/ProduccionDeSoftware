from datetime import date
from typing import TYPE_CHECKING, Dict, Any, Union
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

if TYPE_CHECKING:
    from app.usuario import Usuario

# CLEAN CODE:
# - SRP: La clase `Suscripcion` se encarga de la lógica de negocio relacionada con las suscripciones.
# - Métodos Estáticos: Los métodos son estáticos porque operan sobre los datos sin depender del estado de una instancia particular.
# - Nombres Claros: Los nombres de los métodos (`activar_suscripcion_premium`, `ver_estado_suscripcion`) son autoexplicativos.
# - Manejo de Errores: El código maneja explícitamente los casos de error y devuelve mensajes claros.

class Suscripcion:
    def __init__(self, id_suscripcion: int, usuario_id: int, mes_inicio: int, mes_fin: int, tarifa: int):
        # CLEAN CODE: El constructor es simple y solo asigna valores.
        self.id_suscripcion = id_suscripcion
        self.usuario_id = usuario_id
        self.mes_inicio = mes_inicio
        self.mes_fin = mes_fin
        self.tarifa = tarifa

    @staticmethod
    async def activar_suscripcion_premium(session: AsyncSession, usuario: "Usuario", codigo: str) -> str:
        # CLEAN CODE: Fail-Fast: Las validaciones se realizan al principio del método.
        if not codigo.isdigit() or len(codigo) != 5:
            return "Código inválido. Debe ser un código numérico de 5 dígitos."

        last_digit = int(codigo[-1])
        if last_digit not in [1, 2, 3]:
            return "Código inválido. El último dígito es incorrecto."

        # CLEAN CODE: La lógica de negocio está bien encapsulada y es fácil de entender.
        duracion_map = {1: 1, 2: 3, 3: 6}
        duracion_meses = duracion_map[last_digit]
        tarifa = last_digit
        
        current_month = date.today().month
        mes_fin_calculado = (current_month + duracion_meses - 1) % 12 + 1

        update_user_query = text("UPDATE usuario SET rol = :rol, mes_suscripcion = :mes WHERE id_usuario = :uid")
        insert_sub_query = text("INSERT INTO suscripcion (usuario_id, mes_inicio, mes_fin, tarifa) VALUES (:uid, :inicio, :fin, :tarifa)")

        try:
            # CLEAN CODE: Las transacciones de base de datos son atómicas (todo o nada).
            await session.execute(update_user_query, {"rol": 2, "mes": current_month, "uid": usuario.id_usuario})
            await session.execute(insert_sub_query, {"uid": usuario.id_usuario, "inicio": current_month, "fin": mes_fin_calculado, "tarifa": tarifa})
            await session.commit()
            
            usuario.rol = 2
            usuario.mes_suscripcion = current_month
            return f"Suscripción Premium activada por {duracion_meses} meses."
        except Exception as e:
            await session.rollback()
            return f"Error al activar la suscripción: {e}"

    @staticmethod
    async def ver_estado_suscripcion(session: AsyncSession, usuario: "Usuario") -> Union[Dict[str, Any], str]:
        # CLEAN CODE: El método maneja diferentes casos (roles) de forma clara y estructurada.
        if usuario.rol == 0:
            return {"tarifa": "Vitalicia", "vigente": True}
        
        if usuario.rol == 1:
            return "No tienes una suscripción activa, pásate a Premium."

        if usuario.rol == 2:
            query = text("SELECT mes_inicio, mes_fin, tarifa FROM suscripcion WHERE usuario_id = :uid ORDER BY id_suscripcion DESC LIMIT 1")
            sub_data = (await session.execute(query, {"uid": usuario.id_usuario})).fetchone()

            if not sub_data:
                return "Error: Usuario Premium sin registro de suscripción."

            mes_inicio, mes_fin, tarifa = sub_data
            mes_actual = date.today().month
            
            # CLEAN CODE: La lógica para verificar si la suscripción está activa es clara y maneja el caso de fin de año.
            activa = (mes_inicio <= mes_actual <= mes_fin) if mes_inicio <= mes_fin else (mes_actual >= mes_inicio or mes_actual <= mes_fin)

            return {"tarifa": tarifa, "vigente": activa, "mes_inicio": mes_inicio, "mes_fin": mes_fin}
        
        return "Rol de usuario no reconocido."
