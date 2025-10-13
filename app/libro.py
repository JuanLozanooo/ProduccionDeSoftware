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
        pass

    def obtener_promedio_calificaciones(self, calificaciones: List[float]) -> float:
        pass

    def agregar_review(self, review: 'Review') -> None:
        pass

    def mostrar_reviews(self) -> str:
        pass
