from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.libro import Libro
from app.usuario import Usuario
from app.design_patterns import DesignPatterns

class Administrador:
    def __init__(self, id_admin: int, username: str, email: str, password: str):
        self.id_admin = id_admin
        self.username = username
        self.email = email
        self.password = password

    # Métodos CRUD para Usuario
    async def crear_usuario(self, session: AsyncSession, datos: Dict[str, Any]) -> Usuario:
        datos.setdefault("mes_suscripcion", 0)
        query = text(
            "INSERT INTO usuario (id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion) "
            "VALUES (:id_usuario, :rol, :username, :email_usuario, :password, :activo, :mes_suscripcion)"
        )
        await session.execute(query, datos)
        await session.commit()
        return Usuario(**datos)

    async def consultar_usuario(self, session: AsyncSession, id_usuario: int) -> Optional[Usuario]:
        query = text("SELECT id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion FROM usuario WHERE id_usuario = :id")
        result = await session.execute(query, {"id": id_usuario})
        row = result.first()
        if not row:
            return None
        return Usuario(
            id_usuario=row.id_usuario,
            rol=row.rol,
            username=row.username,
            email_usuario=row.email_usuario,
            password=row.password,
            activo=bool(row.activo),
            mes_suscripcion=row.mes_suscripcion
        )

    async def actualizar_usuario(self, session: AsyncSession, id_usuario: int, campos: Dict[str, Any]) -> None:
        sets = []
        params = {"id": id_usuario}
        for k, v in campos.items():
            sets.append(f"{k} = :{k}")
            params[k] = v
        if not sets:
            return
        query = text(f"UPDATE usuario SET {', '.join(sets)} WHERE id_usuario = :id")
        await session.execute(query, params)
        await session.commit()

    async def eliminar_usuario(self, session: AsyncSession, id_usuario: int) -> bool:
        # Memento: Guardar el estado del usuario antes de eliminarlo
        memento_creado = await DesignPatterns.crear_memento_usuario(session, id_usuario)
        
        if not memento_creado:
            await session.rollback()
            print(f"No se pudo crear el memento. La eliminación del usuario {id_usuario} ha sido cancelada.")
            return False

        # Proceder con la eliminación
        query = text("DELETE FROM usuario WHERE id_usuario = :id")
        try:
            await session.execute(query, {"id": id_usuario})
            await session.commit()
            print(f"Usuario {id_usuario} eliminado correctamente.")
            return True
        except Exception as e:
            await session.rollback()
            print(f"Error al eliminar el usuario {id_usuario} después de crear el memento: {e}")
            return False

    async def gestionar_estado_usuario(self, session: AsyncSession, id_usuario: int, activo: bool) -> None:
        query = text("UPDATE usuario SET activo = :activo WHERE id_usuario = :id")
        await session.execute(query, {"id": id_usuario, "activo": activo})
        await session.commit()

    # Métodos CRUD para Libro
    async def crear_libro(self, session: AsyncSession, datos: Dict[str, Any]) -> Libro:
        datos.setdefault("sinopsis", "")
        query = text(
            "INSERT INTO libro (id_libro, titulo, autor, categoria, anio_publicacion, sinopsis) "
            "VALUES (:id_libro, :titulo, :autor, :categoria, :anio_publicacion, :sinopsis)"
        )
        await session.execute(query, datos)
        await session.commit()
        return Libro(**datos)

    async def consultar_libro(self, session: AsyncSession, id_libro: int) -> Optional[Libro]:
        query = text("SELECT id_libro, titulo, autor, categoria, anio_publicacion, sinopsis FROM libro WHERE id_libro = :id")
        result = await session.execute(query, {"id": id_libro})
        row = result.first()
        if not row:
            return None
        return Libro(
            id_libro=row.id_libro,
            titulo=row.titulo,
            autor=row.autor,
            categoria=row.categoria,
            anio_publicacion=int(row.anio_publicacion),
            sinopsis=row.sinopsis
        )

    async def actualizar_libro(self, session: AsyncSession, id_libro: int, campos: Dict[str, Any]) -> None:
        sets = []
        params = {"id": id_libro}
        for k, v in campos.items():
            sets.append(f"{k} = :{k}")
            params[k] = v
        if not sets:
            return
        query = text(f"UPDATE libro SET {', '.join(sets)} WHERE id_libro = :id")
        await session.execute(query, params)
        await session.commit()

    async def eliminar_libro(self, session: AsyncSession, id_libro: int) -> None:
        query = text("DELETE FROM libro WHERE id_libro = :id")
        await session.execute(query, {"id": id_libro})
        await session.commit()