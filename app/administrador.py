from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.libro import Libro
from app.usuario import Usuario

class Administrador:
    def __init__(self, id_admin: int, username: str, email: str, password: str):
        self.id_admin = id_admin
        self.username = username
        self.email = email
        self.password = password

    # Métodos CRUD para Usuario
    async def crear_usuario(self, session: AsyncSession, datos: Dict[str, Any]) -> Usuario:
        query = text(
            "INSERT INTO usuarios (id_usuario, rol, username, email_usuario, password, activo) "
            "VALUES (:id_usuario, :rol, :username, :email_usuario, :password, :activo)"
        )
        await session.execute(query, datos)
        await session.commit()
        return Usuario(
            id_usuario=datos["id_usuario"],
            rol=datos["rol"],
            username=datos["username"],
            email_usuario=datos["email_usuario"],
            password=datos["password"],
            activo=datos["activo"],
        )

    async def consultar_usuario(self, session: AsyncSession, id_usuario: int) -> Optional[Usuario]:
        query = text("SELECT id_usuario, rol, username, email_usuario, password, activo FROM usuarios WHERE id_usuario = :id")
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
        )

    async def actualizar_usuario(self, session: AsyncSession, id_usuario: int, campos: Dict[str, Any]) -> None:
        sets = []
        params = {"id": id_usuario}
        for k, v in campos.items():
            sets.append(f"{k} = :{k}")
            params[k] = v
        if not sets:
            return
        query = text(f"UPDATE usuarios SET {', '.join(sets)} WHERE id_usuario = :id")
        await session.execute(query, params)
        await session.commit()

    async def eliminar_usuario(self, session: AsyncSession, id_usuario: int) -> None:
        query = text("DELETE FROM usuarios WHERE id_usuario = :id")
        await session.execute(query, {"id": id_usuario})
        await session.commit()

    async def gestionar_estado_usuario(self, session: AsyncSession, id_usuario: int, activo: bool) -> None:
        query = text("UPDATE usuarios SET activo = :activo WHERE id_usuario = :id")
        await session.execute(query, {"id": id_usuario, "activo": activo})
        await session.commit()

    # Métodos CRUD para Libro
    async def crear_libro(self, session: AsyncSession, datos: Dict[str, Any]) -> Libro:
        query = text(
            "INSERT INTO libros (id_libro, titulo, autor, categoria, anio_publicacion) "
            "VALUES (:id_libro, :titulo, :autor, :categoria, :anio_publicacion)"
        )
        await session.execute(query, datos)
        await session.commit()
        return Libro(
            id_libro=datos["id_libro"],
            titulo=datos["titulo"],
            autor=datos["autor"],
            categoria=datos["categoria"],
            anio_publicacion=datos["anio_publicacion"],
        )

    async def consultar_libro(self, session: AsyncSession, id_libro: int) -> Optional[Libro]:
        query = text("SELECT id_libro, titulo, autor, categoria, anio_publicacion FROM libros WHERE id_libro = :id")
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
        )

    async def actualizar_libro(self, session: AsyncSession, id_libro: int, campos: Dict[str, Any]) -> None:
        sets = []
        params = {"id": id_libro}
        for k, v in campos.items():
            sets.append(f"{k} = :{k}")
            params[k] = v
        if not sets:
            return
        query = text(f"UPDATE libros SET {', '.join(sets)} WHERE id_libro = :id")
        await session.execute(query, params)
        await session.commit()

    async def eliminar_libro(self, session: AsyncSession, id_libro: int) -> None:
        query = text("DELETE FROM libros WHERE id_libro = :id")
        await session.execute(query, {"id": id_libro})
        await session.commit()