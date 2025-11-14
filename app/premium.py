from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.usuario import Usuario
from app.libro import Libro

class UsuarioPago(Usuario):
    def __init__(self, id_usuario: int, username: str, email_usuario: str, password: str, activo: bool = True):
        super().__init__(id_usuario, rol=2, username=username, email_usuario=email_usuario, password=password, activo=activo)

    def leer_libro_completo(self, libro: Libro) -> dict:
        if self.rol not in [0, 2]:
            return {"error": "Acceso denegado. Función solo para usuarios Premium."}
        
        return {
            "titulo": libro.titulo,
            "autor": libro.autor,
            "contenido": libro.sinopsis
        }

    async def cancelar_suscripcion(self, session: AsyncSession) -> dict:
        if self.rol != 2:
            return {"mensaje": "El usuario no es Premium."}

        query = text("UPDATE usuario SET rol = 1 WHERE id_usuario = :id")
        try:
            await session.execute(query, {"id": self.id_usuario})
            await session.commit()
            self.rol = 1
            return {"mensaje": "Suscripción cancelada. Su rol ha sido cambiado a gratuito."}
        except Exception as e:
            await session.rollback()
            return {"error": f"No se pudo cancelar la suscripción: {e}"}
