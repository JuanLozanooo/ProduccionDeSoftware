from typing import List

class Review:
    id_review: int
    usuario_id: int
    libro_id: int
    comentario: str
    calificacion: int
    calificaciones_usuarios: List[float] = []

    def subir_review(self) -> None:
        pass

    def eliminar_review(self) -> None:
        pass
