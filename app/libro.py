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
        if not calificaciones:
            return 0.0
        promedio = sum(calificaciones) / len(calificaciones)
        Libro.calificacion_promedio = round(promedio, 2)
        return Libro.calificacion_promedio

    def agregar_review(self, review: 'Review') -> None:
        Libro.lista_reviews.append(review)
        review.subir_review()

    def mostrar_reviews(self) -> str:
        if not Libro.lista_reviews:
            return "Sin reviews"
        detalles = [f"[{r.usuario_id}->{r.libro_id}] {r.calificacion}/5: {r.comentario}" for r in Libro.lista_reviews]
        return "\n".join(detalles)
