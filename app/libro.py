from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.design_patterns import DesignPatterns, ReviewConcreto, ReviewVerificadaDecorator
from app.review import Review

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
        query_reviews = text(
            "SELECT r.id_review, r.usuario_id, r.libro_id, r.comentario "
            "FROM review r WHERE r.libro_id = :id_libro"
        )
        result_reviews = await session.execute(query_reviews, {"id_libro": self.id_libro})
        reviews_data = result_reviews.fetchall()

        if not reviews_data:
            return "Sin reviews"

        reviews_decoradas = []
        for review_data in reviews_data:
            review = Review(**review_data)

            query_user = text("SELECT rol FROM usuario WHERE id_usuario = :usuario_id")
            result_user = await session.execute(query_user, {"usuario_id": review.usuario_id})
            user_role = result_user.scalar()

            es_premium = (user_role == 2)
            
            review_component = DesignPatterns.decorar_review(review, es_premium)
            
            query_username = text("SELECT username FROM usuario WHERE id_usuario = :usuario_id")
            result_username = await session.execute(query_username, {"usuario_id": review.usuario_id})
            username = result_username.scalar()
            
            reviews_decoradas.append(f"[{username}] {review_component.mostrar()}")

        return "\n".join(reviews_decoradas)
