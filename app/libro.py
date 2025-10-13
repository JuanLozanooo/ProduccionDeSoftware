from typing import List
from app.review import Review

class Libro:
    id_libro: int
    titulo: str
    autor: str
    categoria: str
    anio_publicacion: int
    lista_reviews: List[Review] = []
    calificacion_promedio: float = 0.0

    def obtener_descripción(self) -> str:
        pass

    def obtener_promedio_calificaciones(self, calificaciones: List[float]) -> float:
        pass

    def agregar_review(self, review: 'Review') -> None:
        pass

    def mostrar_reviews(self) -> str:
        pass
