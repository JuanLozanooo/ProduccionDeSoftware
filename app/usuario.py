from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.libro import Libro
from app.design_patterns import DesignPatterns

# CLEAN CODE:
# - SRP: La clase `Usuario` se centra en la gestión de la información y acciones de un usuario.
# - Cohesión Alta: Todos los métodos y atributos están directamente relacionados con la entidad `Usuario`.
# - Nombres Descriptivos: Los nombres de los métodos (`iniciar_sesion`, `buscar_libro`) son claros y predecibles.
# - Encapsulación: La lógica de negocio, como la autenticación y la gestión de la sesión, está contenida en la clase.

class Usuario:
    def __init__(self, id_usuario: int, rol: int, username: str, email_usuario: str, password: str, activo: bool = True, mes_suscripcion: int = 0):
        # CLEAN CODE: El constructor es simple y solo asigna valores. Los valores por defecto mejoran la usabilidad.
        self.id_usuario = id_usuario
        self.rol = rol
        self.username = username
        self.email_usuario = email_usuario
        self.password = password
        self.activo = activo
        self.mes_suscripcion = mes_suscripcion

    async def iniciar_sesion(self, session: AsyncSession) -> dict:
        # CLEAN CODE: El método tiene una única responsabilidad: autenticar al usuario.
        query = text("SELECT * FROM usuario WHERE username = :username LIMIT 1")
        result = await session.execute(query, {"username": self.username})
        row = result.first()

        # CLEAN CODE: La comparación de contraseñas es robusta al ignorar espacios en blanco.
        if not row or str(row.password).strip() != str(self.password).strip():
            return {"autenticado": False, "mensaje": "Credenciales inválidas"}

        # CLEAN CODE: Fail-Fast: Se verifica el estado de activación del usuario antes de continuar.
        if not bool(row.activo):
            return {"autenticado": False, "mensaje": "Usuario inactivo"}

        # CLEAN CODE: El estado del objeto se actualiza después de una autenticación exitosa.
        self.id_usuario = row.id_usuario
        self.rol = row.rol
        self.username = row.username
        self.email_usuario = row.email_usuario
        self.activo = bool(row.activo)
        self.mes_suscripcion = int(row.mes_suscripcion)

        # CLEAN CODE: La lógica para determinar el menú del usuario está bien estructurada y es fácil de leer.
        menu_basico = ["buscar_libro", "ver_reviews_libro", "agregar_review_libro"]
        menu_gratuito = ["leer_fragmento_libro"]
        menu_premium = ["leer_libro_completo", "descargar_libro"]
        menu_admin = ["crear_usuario", "consultar_usuario", "actualizar_usuario", "eliminar_usuario", "crear_libro", "consultar_libro", "actualizar_libro", "eliminar_libro", "gestionar_estado_usuario"]

        menu_roles = {
            0: menu_basico + menu_gratuito + menu_premium + menu_admin,
            1: menu_basico + menu_gratuito,
            2: menu_basico + menu_premium,
        }
        menu = menu_roles.get(self.rol, menu_basico)

        return {"autenticado": True, "usuario": self.__dict__, "menu_habilitado": menu}

    async def cerrar_sesion(self) -> dict:
        # CLEAN CODE: Método simple y con un propósito claro.
        return {"mensaje": "Sesión cerrada correctamente"}

    async def buscar_libro(self, session: AsyncSession, search_term: str) -> Optional[Libro]:
        # CLEAN CODE: Delega la lógica de búsqueda a un patrón de diseño, manteniendo la clase Usuario desacoplada.
        return await DesignPatterns.busqueda_cadena_de_responsabilidad(session, search_term)

    async def cambiar_username(self, session: AsyncSession, nuevo_username: str) -> dict:
        # CLEAN CODE: El método es conciso y se enfoca en una sola tarea.
        await session.execute(text("UPDATE usuario SET username = :nuevo WHERE id_usuario = :id"), {"nuevo": nuevo_username, "id": self.id_usuario})
        await session.commit()
        self.username = nuevo_username
        return {"username": self.username}

    async def cambiar_contrasena(self, session: AsyncSession, nueva_contrasena: str) -> dict:
        # CLEAN CODE: Similar al anterior, es un método simple y enfocado.
        await session.execute(text("UPDATE usuario SET password = :pwd WHERE id_usuario = :id"), {"pwd": nueva_contrasena, "id": self.id_usuario})
        await session.commit()
        self.password = nueva_contrasena
        return {"contrasena_actualizada": True}
