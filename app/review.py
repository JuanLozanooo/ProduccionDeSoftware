from typing import Optional, TYPE_CHECKING
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

if TYPE_CHECKING:
    from app.libro import Libro
    from app.usuario import Usuario

# CLEAN CODE:
# - SRP: La clase `Review` se encarga únicamente de representar y gestionar una review.
# - Cohesión Alta: Todos los atributos y métodos están directamente relacionados con una review.
# - Nombres Descriptivos: El nombre del método `subir_review` es claro y conciso.
# - Encapsulación: La lógica para guardar la review en la base de datos está contenida en la clase.

class Review:
    def __init__(self, comentario: str, id_review: Optional[int] = None, usuario_id: Optional[int] = None, libro_id: Optional[int] = None):
        # CLEAN CODE: El constructor es simple y solo asigna los valores iniciales.
        self.id_review = id_review
        self.comentario = comentario
        self.usuario_id = usuario_id
        self.libro_id = libro_id

    async def subir_review(self, session: AsyncSession, usuario: "Usuario", libro: "Libro") -> None:
        # CLEAN CODE: El método tiene una única responsabilidad: subir una review a la base de datos.
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
            # CLEAN CODE: El manejo de la sesión y la transacción es claro y conciso.
            result = await session.execute(query, params)
            self.id_review = result.scalar_one()
            await session.commit()
        except Exception as e:
            await session.rollback()
            # CLEAN CODE: El manejo de errores es explícito y proporciona información útil.
            print(f"Error al guardar review en la BD: {e}")
