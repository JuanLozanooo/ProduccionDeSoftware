from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.review import Review
from typing import List, Dict, Any

# CLEAN CODE:
# - SRP: La clase `Libro` se centra en representar un libro y sus operaciones relacionadas.
# - Cohesión Alta: Todos los métodos y atributos de la clase están directamente relacionados con un libro.
# - Nombres Descriptivos: Los nombres de los métodos (`obtener_descripción`, `mostrar_reviews`) son claros y predecibles.
# - Encapsulación: La lógica para mostrar las reviews está contenida dentro de la clase, ocultando la complejidad.

class Libro:
    def __init__(self, id_libro: int, titulo: str, autor: str, categoria: str, anio_publicacion: int, sinopsis: str):
        # CLEAN CODE: El constructor es simple y se limita a la asignación de atributos.
        self.id_libro = id_libro
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.anio_publicacion = anio_publicacion
        self.sinopsis = sinopsis

    def obtener_descripción(self) -> str:
        # CLEAN CODE: Método pequeño y con una única responsabilidad: formatear la descripción.
        return f"{self.titulo} de {self.autor} ({self.anio_publicacion}) - Categoría: {self.categoria}"

    async def get_reviews(self, session: AsyncSession) -> List[Dict[str, Any]]:
        from app.design_patterns import DesignPatterns
        
        query_reviews = text(
            "SELECT r.id_review, r.usuario_id, r.libro_id, r.comentario, u.username, u.rol "
            "FROM review r JOIN usuario u ON r.usuario_id = u.id_usuario "
            "WHERE r.libro_id = :id_libro"
        )
        result_reviews = await session.execute(query_reviews, {"id_libro": self.id_libro})
        reviews_data = result_reviews.mappings().fetchall()

        reviews_list = []
        for review_data in reviews_data:
            # FIX: Create the Review object with only the arguments it expects.
            review = Review(
                id_review=review_data['id_review'],
                usuario_id=review_data['usuario_id'],
                libro_id=review_data['libro_id'],
                comentario=review_data['comentario']
            )
            es_premium = (review_data['rol'] == 2)
            review_component = DesignPatterns.decorar_review(review, es_premium)
            reviews_list.append({
                "username": review_data['username'],
                "comentario": review_component.mostrar()
            })
        return reviews_list

    async def mostrar_reviews(self, session: AsyncSession) -> str:
        reviews = await self.get_reviews(session)
        if not reviews:
            return "Sin reviews"
        
        detalles = [f"[{review['username']}] {review['comentario']}" for review in reviews]
        return "\n".join(detalles)
