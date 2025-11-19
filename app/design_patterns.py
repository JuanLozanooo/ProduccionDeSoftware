from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from typing import Optional, List
from app.libro import Libro
import abc

# CLEAN CODE:
# - Abstracción: Se utilizan clases abstractas (Handler, ReviewComponent) para definir contratos claros.
# - Principio de Abierto/Cerrado (OCP): La cadena de responsabilidad y el decorador se pueden extender sin modificar el código existente.
# - Nombres significativos: Los nombres de las clases (TituloHandler, ReviewVerificadaDecorator) describen su propósito.
# - SRP: Cada clase de handler tiene una única responsabilidad (buscar por un criterio específico).
# - Código Organizado: El código está agrupado por patrón de diseño, mejorando la legibilidad.

# --- CHAIN OF RESPONSIBILITY ---

class Handler(abc.ABC):
    # CLEAN CODE: Define una interfaz común para todos los manejadores.
    @abc.abstractmethod
    def set_next(self, handler):
        pass

    @abc.abstractmethod
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        pass

class AbstractHandler(Handler):
    # CLEAN CODE: Implementación base que evita la duplicación de la lógica de la cadena.
    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        if self._next_handler:
            return await self._next_handler.handle(request, session)
        return None

class TituloHandler(AbstractHandler):
    # CLEAN CODE: Clase cohesiva y con una única responsabilidad: buscar por título.
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        search_term = request.strip().lower()
        query = text("SELECT * FROM libro WHERE LOWER(titulo) LIKE :titulo LIMIT 1")
        result = await session.execute(query, {"titulo": f"%{search_term}%"})
        row = result.first()
        if row:
            return Libro(**row)
        return await super().handle(request, session)

class AutorHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        search_term = request.strip().lower()
        query = text("SELECT * FROM libro WHERE LOWER(autor) LIKE :autor LIMIT 1")
        result = await session.execute(query, {"autor": f"%{search_term}%"})
        row = result.first()
        if row:
            return Libro(**row)
        return await super().handle(request, session)

class CategoriaHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        search_term = request.strip().lower()
        query = text("SELECT * FROM libro WHERE LOWER(categoria) LIKE :categoria LIMIT 1")
        result = await session.execute(query, {"categoria": f"%{search_term}%"})
        row = result.first()
        if row:
            return Libro(**row)
        return await super().handle(request, session)

class AnioHandler(AbstractHandler):
    async def handle(self, request: str, session: AsyncSession) -> Optional[Libro]:
        search_term = request.strip()
        if search_term.isdigit():
            query = text("SELECT * FROM libro WHERE anio_publicacion = :anio LIMIT 1")
            result = await session.execute(query, {"anio": int(search_term)})
            row = result.first()
            if row:
                return Libro(**row)
        return await super().handle(request, session)

class DesignPatterns:
    # CLEAN CODE: Fachada simple que oculta la complejidad de la creación de los patrones.

    # --- MEMENTO ---
    @staticmethod
    async def crear_memento_usuario(session: AsyncSession, id_usuario: int) -> bool:
        # CLEAN CODE: El nombre del método explica claramente su intención (Command-Query Separation).
        query_select = text("SELECT * FROM usuario WHERE id_usuario = :id")
        usuario_data = (await session.execute(query_select, {"id": id_usuario})).mappings().first()

        if not usuario_data:
            return False

        query_insert = text(
            "INSERT INTO eliminados (id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion) "
            "VALUES (:id_usuario, :rol, :username, :email_usuario, :password, :activo, :mes_suscripcion)"
        )
        await session.execute(query_insert, dict(usuario_data))
        return True

    # --- DECORATOR ---
    @staticmethod
    def decorar_review(review, es_premium):
        # CLEAN CODE: Fábrica simple que facilita la creación de decoradores.
        component = ReviewConcreto(review)
        if es_premium:
            return ReviewVerificadaDecorator(component)
        return component

    # --- CHAIN OF RESPONSIBILITY ---
    @staticmethod
    async def busqueda_cadena_de_responsabilidad(session: AsyncSession, search_term: str) -> Optional[Libro]:
        # CLEAN CODE: Encapsula la creación y el orden de la cadena.
        titulo_handler = TituloHandler()
        autor_handler = AutorHandler()
        categoria_handler = CategoriaHandler()
        anio_handler = AnioHandler()

        titulo_handler.set_next(autor_handler).set_next(categoria_handler).set_next(anio_handler)
        return await titulo_handler.handle(search_term, session)

# --- DECORATOR IMPLEMENTATION ---

class ReviewComponent(abc.ABC):
    # CLEAN CODE: Componente base del decorador.
    @abc.abstractmethod
    def mostrar(self):
        pass

class ReviewConcreto(ReviewComponent):
    # CLEAN CODE: Objeto base que se va a decorar.
    def __init__(self, review):
        self._review = review

    def mostrar(self):
        return self._review.comentario

class ReviewDecorator(ReviewComponent):
    # CLEAN CODE: Decorador base que sigue la misma interfaz que el componente.
    def __init__(self, review_component):
        self._review_component = review_component

    def mostrar(self):
        return self._review_component.mostrar()

class ReviewVerificadaDecorator(ReviewDecorator):
    # CLEAN CODE: Decorador concreto que añade una funcionalidad específica.
    def mostrar(self):
        return f"⭐ [Verificada] {super().mostrar()}"
