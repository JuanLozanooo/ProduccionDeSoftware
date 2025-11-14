from typing import Optional, TYPE_CHECKING
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

if TYPE_CHECKING:
    from app.libro import Libro
    from app.usuario import Usuario

class Review:
    def __init__(self, comentario: str, id_review: Optional[int] = None):
        self.id_review = id_review
        self.comentario = comentario
        self.usuario_id: Optional[int] = None
        self.libro_id: Optional[int] = None

    async def subir_review(self, session: AsyncSession, usuario: "Usuario", libro: "Libro") -> None:
        self.usuario_id = usuario.id_usuario
        self.libro_id = libro.id_libro

        query = text(
            "INSERT INTO review (usuario_id, libro_id, comentario) "
            "VALUES (:uid, :lid, :com) "
            "RETURNING id_review"
        )

        params = {
            "uid": self.usuario_id,
            "lid": self.libro_id,
            "com": self.comentario
        }

        try:
            result = await session.execute(query, params)
            new_id = result.scalar_one()
            self.id_review = new_id
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Error al guardar review en la BD: {e}")