from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.usuario import Usuario

class UsuarioPago(Usuario):
    def __init__(self, id_usuario: int, username: str, email_usuario: str, password: str,
                 tipo_suscripcion: int, activo: bool = True):
        super().__init__(id_usuario, rol=2, username=username, email_usuario=email_usuario, password=password, activo=activo)
        self.tipo_suscripcion = tipo_suscripcion

    async def leer_libro_completo(self, session: AsyncSession, id_libro: int) -> dict:
        query = text("SELECT id_libro, titulo, autor, categoria, anio_publicacion FROM libro WHERE id_libro = :id")
        result = await session.execute(query, {"id": id_libro})
        row = result.first()
        if not row:
            return {"mensaje": "Libro no encontrado"}
        contenido = f"Contenido completo simulado de '{row.titulo}' por {row.autor}."
        return {"id_libro": row.id_libro, "contenido": contenido}

    async def renovar_suscripcion(self) -> dict:
        return {"mensaje": "Suscripción renovada correctamente."}

    async def cancelar_suscripcion(self) -> dict:
        self.activo = False
        return {"mensaje": "Suscripción cancelada."}