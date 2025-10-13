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
        pass

    def eliminar_review(self) -> None:
        pass
