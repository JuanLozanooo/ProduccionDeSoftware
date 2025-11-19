from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.review import Review

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

    async def mostrar_reviews(self, session: AsyncSession) -> str:
        # CLEAN CODE: La importación del decorador se hace aquí para evitar importaciones circulares.
        from app.design_patterns import DesignPatterns
        
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
            # CLEAN CODE: La lógica de decoración está delegada al patrón de diseño, manteniendo este método enfocado.
            review = Review(**review_data)

            query_user_role = text("SELECT rol FROM usuario WHERE id_usuario = :usuario_id")
            user_role = (await session.execute(query_user_role, {"usuario_id": review.usuario_id})).scalar()
            
            es_premium = (user_role == 2)
            review_component = DesignPatterns.decorar_review(review, es_premium)
            
            query_username = text("SELECT username FROM usuario WHERE id_usuario = :usuario_id")
            username = (await session.execute(query_username, {"usuario_id": review.usuario_id})).scalar()
            
            reviews_decoradas.append(f"[{username}] {review_component.mostrar()}")

        return "\n".join(reviews_decoradas)
