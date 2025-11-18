from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from typing import Optional, List
from app.libro import Libro
import abc

# ---------- CHAIN OF RESPONSIBILITY ----------
class Handler(abc.ABC):
    @abc.abstractmethod
    def set_next(self, handler):
        pass

    @abc.abstractmethod
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        pass

class AbstractHandler(Handler):
    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        if self._next_handler:
            return await self._next_handler.handle(request, session)
        return None

class TituloHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        query = text("SELECT * FROM libro WHERE LOWER(titulo) LIKE LOWER(:titulo) LIMIT 1")
        result = await session.execute(query, {"titulo": f"%{request}%"})
        row = result.first()
        if row:
            return Libro(id_libro=row.id_libro, titulo=row.titulo, autor=row.autor, categoria=row.categoria, anio_publicacion=row.anio_publicacion, sinopsis=row.sinopsis)
        return await super().handle(request, session)

class AutorHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        query = text("SELECT * FROM libro WHERE LOWER(autor) LIKE LOWER(:autor) LIMIT 1")
        result = await session.execute(query, {"autor": f"%{request}%"})
        row = result.first()
        if row:
            return Libro(id_libro=row.id_libro, titulo=row.titulo, autor=row.autor, categoria=row.categoria, anio_publicacion=row.anio_publicacion, sinopsis=row.sinopsis)
        return await super().handle(request, session)

class CategoriaHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        query = text("SELECT * FROM libro WHERE LOWER(categoria) LIKE LOWER(:categoria) LIMIT 1")
        result = await session.execute(query, {"categoria": f"%{request}%"})
        row = result.first()
        if row:
            return Libro(id_libro=row.id_libro, titulo=row.titulo, autor=row.autor, categoria=row.categoria, anio_publicacion=row.anio_publicacion, sinopsis=row.sinopsis)
        return await super().handle(request, session)

class AnioHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        if request.isdigit():
            query = text("SELECT * FROM libro WHERE anio_publicacion = :anio LIMIT 1")
            result = await session.execute(query, {"anio": int(request)})
            row = result.first()
            if row:
                return Libro(id_libro=row.id_libro, titulo=row.titulo, autor=row.autor, categoria=row.categoria, anio_publicacion=row.anio_publicacion, sinopsis=row.sinopsis)
        return await super().handle(request, session)

class DesignPatterns:

    # ---------- MEMENTO ----------
    @staticmethod
    async def crear_memento_usuario(session: AsyncSession, id_usuario: int) -> bool:
        """
        Crea un 'memento' de un usuario antes de ser eliminado, guardándolo en la tabla 'eliminados'.
        """
        # 1. Encontrar el usuario a eliminar en la tabla principal
        query_select = text("SELECT * FROM usuario WHERE id_usuario = :id")
        result = await session.execute(query_select, {"id": id_usuario})
        usuario_data = result.mappings().first()

        if not usuario_data:
            print(f"Error: Usuario con ID {id_usuario} no encontrado para crear memento.")
            return False

        # 2. Insertar los datos del usuario en la tabla 'eliminados'
        query_insert = text(
            "INSERT INTO eliminados (id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion) "
            "VALUES (:id_usuario, :rol, :username, :email_usuario, :password, :activo, :mes_suscripcion)"
        )
        try:
            await session.execute(query_insert, dict(usuario_data))
            print(f"Memento creado para el usuario ID {id_usuario}.")
            return True
        except Exception as e:
            print(f"Error al crear memento para el usuario ID {id_usuario}: {e}")
            return False

    @staticmethod
    async def restaurar_usuario_desde_memento(session: AsyncSession, id_usuario: int) -> bool:
        """
        Restaura un usuario desde la tabla 'eliminados' (el memento) a la tabla 'usuario'.
        """
        # 1. Encontrar el memento en la tabla 'eliminados'
        query_select = text("SELECT * FROM eliminados WHERE id_usuario = :id")
        result = await session.execute(query_select, {"id": id_usuario})
        memento_data = result.mappings().first()

        if not memento_data:
            print(f"Error: Memento para el usuario ID {id_usuario} no encontrado.")
            return False

        # 2. Re-insertar el usuario en la tabla 'usuario'
        query_insert = text(
            "INSERT INTO usuario (id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion) "
            "VALUES (:id_usuario, :rol, :username, :email_usuario, :password, :activo, :mes_suscripcion)"
        )
        
        # 3. Eliminar el memento de la tabla 'eliminados'
        query_delete = text("DELETE FROM eliminados WHERE id_usuario = :id")

        try:
            # Se ejecuta como una transacción: si algo falla, todo se revierte.
            await session.execute(query_insert, dict(memento_data))
            await session.execute(query_delete, {"id": id_usuario})
            await session.commit()
            print(f"Usuario ID {id_usuario} restaurado desde memento.")
            return True
        except Exception as e:
            await session.rollback()
            print(f"Error al restaurar usuario ID {id_usuario} desde memento: {e}")
            return False

    # ---------- DECORATOR ----------
    @staticmethod
    def decorar_review(review, es_premium):
        if es_premium:
            return ReviewVerificadaDecorator(ReviewConcreto(review))
        return ReviewConcreto(review)

    # ---------- CHAIN OF RESPONSIBILITY ----------
    @staticmethod
    async def busqueda_cadena_de_responsabilidad(session: AsyncSession, search_term: str) -> Optional[Libro]:
        titulo_handler = TituloHandler()
        autor_handler = AutorHandler()
        categoria_handler = CategoriaHandler()
        anio_handler = AnioHandler()

        titulo_handler.set_next(autor_handler).set_next(categoria_handler).set_next(anio_handler)

        return await titulo_handler.handle(search_term, session)

# --- Decorator Implementation ---

class ReviewComponent(abc.ABC):
    @abc.abstractmethod
    def mostrar(self):
        pass

class ReviewConcreto(ReviewComponent):
    def __init__(self, review):
        self._review = review

    def mostrar(self):
        return self._review.comentario

class ReviewDecorator(ReviewComponent):
    def __init__(self, review_component):
        self._review_component = review_component

    def mostrar(self):
        return self._review_component.mostrar()

class ReviewVerificadaDecorator(ReviewDecorator):
    def mostrar(self):
        return f"⭐ [Verificada] {self._review_component.mostrar()}"
