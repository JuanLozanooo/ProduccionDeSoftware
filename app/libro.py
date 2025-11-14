from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

class Libro:
    def __init__(self, id_libro: int, titulo: str, autor: str, categoria: str, anio_publicacion: int, sinopsis: str):
        self.id_libro = id_libro
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.anio_publicacion = anio_publicacion
        self.sinopsis = sinopsis

    def obtener_descripción(self) -> str:
        return f"{self.titulo} de {self.autor} ({self.anio_publicacion}) - Categoría: {self.categoria}"

    async def mostrar_reviews(self, session: AsyncSession) -> str:
        query = text(
            "SELECT u.username, r.comentario "
            "FROM review r JOIN usuario u ON r.usuario_id = u.id_usuario "
            "WHERE r.libro_id = :id_libro"
        )

        result = await session.execute(query, {"id_libro": self.id_libro})
        rows = result.fetchall()

        if not rows:
            return "Sin reviews"

        detalles = [f"[Usuario: {row.username}] {row.comentario}" for row in rows]
        return "\n".join(detalles)