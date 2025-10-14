from typing import List

class Review:
    calificaciones_usuarios: List[float] = []

    def __init__(self, id_review: int, usuario_id: int, libro_id: int, comentario: str, calificacion: int):
        self.id_review = id_review
        self.usuario_id = usuario_id
        self.libro_id = libro_id
        self.comentario = comentario
        self.calificacion = calificacion

    def subir_review(self) -> None:
        # Mantener registro histórico de calificaciones
        Review.calificaciones_usuarios.append(float(self.calificacion))
        # Conectar con Libro: agregar esta review a la lista de reviews del libro
        from app.libro import Libro
        libro_tmp = next((l for l in getattr(Libro, "lista_reviews", []) if getattr(l, "libro_id", None) == self.libro_id), None)
        # Siempre delegar al método del modelo Libro (crea el contenedor temporal si no hay libros cargados)
        lib = Libro(self.libro_id, "", "", "", 0)
        lib.agregar_review(self)

    def eliminar_review(self) -> None:
        if Review.calificaciones_usuarios:
            Review.calificaciones_usuarios.pop()
