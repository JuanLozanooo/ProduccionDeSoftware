from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.libro import Libro


class Usuario:
    def __init__(self, id_usuario: int, rol: int, username: str, email_usuario: str, password: str, activo: bool = True,
                 mes_suscripcion: int = 0):
        self.id_usuario = id_usuario
        self.rol = rol
        self.username = username
        self.email_usuario = email_usuario
        self.password = password
        self.activo = activo
        self.mes_suscripcion = mes_suscripcion

    async def iniciar_sesion(self, session: AsyncSession) -> dict:
        query = text(
            "SELECT id_usuario, rol, username, email_usuario, password, activo, mes_suscripcion "
            "FROM usuario WHERE username = :username LIMIT 1"
        )
        result = await session.execute(query, {"username": self.username})
        row = result.first()
        if not row or str(row.password) != str(self.password):
            return {"autenticado": False, "mensaje": "Credenciales inválidas"}

        self.id_usuario = row.id_usuario
        self.rol = row.rol
        self.username = row.username
        self.email_usuario = row.email_usuario
        self.activo = bool(row.activo)
        self.mes_suscripcion = int(row.mes_suscripcion)

        if not self.activo:
            return {"autenticado": False, "mensaje": "Usuario inactivo"}

        menu_basico: List[str] = [
            "buscar_libro",
            "ver_reviews_libro",
            "agregar_review_libro"
        ]
        menu_gratuito: List[str] = ["leer_fragmento_libro"]
        menu_premium: List[str] = ["leer_libro_completo", "descargar_libro"]
        menu_admin: List[str] = [
            "crear_usuario",
            "consultar_usuario",
            "actualizar_usuario",
            "eliminar_usuario",
            "crear_libro",
            "consultar_libro",
            "actualizar_libro",
            "eliminar_libro",
            "gestionar_estado_usuario"
        ]

        if self.rol == 0:
            menu = menu_basico + menu_gratuito + menu_premium + menu_admin
        elif self.rol == 1:
            menu = menu_basico + menu_gratuito
        elif self.rol == 2:
            menu = menu_basico + menu_premium
        else:
            menu = menu_basico

        return {
            "autenticado": True,
            "usuario": {
                "id_usuario": self.id_usuario,
                "rol": self.rol,
                "username": self.username,
                "email_usuario": self.email_usuario,
                "mes_suscripcion": self.mes_suscripcion
            },
            "menu_habilitado": menu
        }

    async def cerrar_sesion(self) -> dict:
        """ Cierra la sesión del usuario. """
        return {"mensaje": "Sesión cerrada correctamente"}

    async def buscar_libro(self, session: AsyncSession, titulo: Optional[str] = None,
                           autor: Optional[str] = None, categoria: Optional[str] = None) -> Optional[Libro]:
        clauses = []
        params = {}
        if titulo:
            clauses.append("LOWER(titulo) LIKE LOWER(:titulo)")
            params["titulo"] = f"%{titulo}%"
        if autor:
            clauses.append("LOWER(autor) LIKE LOWER(:autor)")
            params["autor"] = f"%{autor}%"
        if categoria:
            clauses.append("LOWER(categoria) LIKE LOWER(:categoria)")
            params["categoria"] = f"%{categoria}%"

        where = ""
        if clauses:
            where = "WHERE " + " AND ".join(clauses)

        query = text(
            f"SELECT id_libro, titulo, autor, categoria, anio_publicacion FROM libro {where} ORDER BY id_libro LIMIT 1"
        )
        result = await session.execute(query, params)
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

    async def cambiar_username(self, session: AsyncSession, nuevo_username: str) -> dict:
        """ Cambia el nombre de usuario. """
        await session.execute(
            text("UPDATE usuario SET username = :nuevo WHERE id_usuario = :id"),
            {"nuevo": nuevo_username, "id": self.id_usuario}
        )
        await session.commit()
        self.username = nuevo_username
        return {"username": self.username}

    async def cambiar_contrasena(self, session: AsyncSession, nueva_contrasena: str) -> dict:
        """ Cambia la contraseña del usuario. """
        await session.execute(
            text("UPDATE usuario SET password = :pwd WHERE id_usuario = :id"),
            {"pwd": nueva_contrasena, "id": self.id_usuario}
        )
        await session.commit()
        self.password = nueva_contrasena
        return {"contrasena_actualizada": True}