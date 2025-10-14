from typing import List
from app.review import Review

class Libro:
    lista_reviews = []
    calificacion_promedio = 0.0

    def __init__(self, id_libro: int, titulo: str, autor: str, categoria: str, anio_publicacion: int):
        self.id_libro = id_libro
        self.titulo = titulo
        self.autor = autor
        self.categoria = categoria
        self.anio_publicacion = anio_publicacion

    def obtener_descripción(self) -> str:
        return f"{self.titulo} de {self.autor} ({self.anio_publicacion}) - Categoría: {self.categoria}"

    def obtener_promedio_calificaciones(self, calificaciones: List[float]) -> float:
        # Ignora el parámetro entrante y calcula con las reviews conectadas de este libro
        califs = [float(r.calificacion) for r in Libro.lista_reviews if getattr(r, "libro_id", None) == self.id_libro]
        if not califs:
            Libro.calificacion_promedio = 0.0
            return 0.0
        promedio = sum(califs) / len(califs)
        Libro.calificacion_promedio = round(promedio, 2)
        return Libro.calificacion_promedio

    def agregar_review(self, review: 'Review') -> None:
        # Evitar duplicados exactos por id_review
        if not any(getattr(r, "id_review", None) == review.id_review for r in Libro.lista_reviews):
            Libro.lista_reviews.append(review)

    def mostrar_reviews(self) -> str:
        reviews_libro = [r for r in Libro.lista_reviews if getattr(r, "libro_id", None) == self.id_libro]
        if not reviews_libro:
            return "Sin reviews"
        detalles = [f"[{r.usuario_id}->{r.libro_id}] {r.calificacion}/5: {r.comentario}" for r in reviews_libro]
        return "\n".join(detalles)
