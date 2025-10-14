from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.usuario import Usuario
from app.suscripcion import Suscripcion
from datetime import date

class Gratuito(Usuario):
    async def leer_fragmento_libro(self, session: AsyncSession, id_libro: int) -> dict:
        query = text("SELECT id_libro, titulo, autor, categoria, anio_publicacion FROM libro WHERE id_libro = :id")
        result = await session.execute(query, {"id": id_libro})
        row = result.first()
        if not row:
            return {"mensaje": "Libro no encontrado"}
        fragmento = f"{row.titulo} - {row.autor} ({row.anio_publicacion}): Inicio de muestra..."
        return {"id_libro": row.id_libro, "fragmento": fragmento}

    async def pasar_a_premium(self, session: AsyncSession, codigo: str) -> dict:
        if not (isinstance(codigo, str) and len(codigo) == 10 and codigo.isdigit()):
            return {"mensaje": "Cupón inválido, inténtalo de nuevo."}

        await session.execute(
            text("UPDATE usuario SET rol = :rol WHERE id_usuario = :id"),
            {"rol": 2, "id": self.id_usuario}
        )
        await session.commit()

        self.rol = 2

        sus = Suscripcion(
            id_suscripcion=int(date.today().strftime("%Y%m%d")),
            usuario_id=self.id_usuario,
            tipo_plan="gratuito",
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            tarifa=0
        )
        sus.activar_suscripcion_premium()

        return {
            "mensaje": "¡Suscripción Premium activada correctamente!",
            "usuario_id": self.id_usuario,
            "rol": self.rol,
            "suscripcion": sus.ver_estado_suscripcion()
        }
