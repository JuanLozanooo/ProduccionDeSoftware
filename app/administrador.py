from typing import Optional, Dict, Any
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession
from app.libro import Libro
from app.usuario import Usuario
from app.design_patterns import DesignPatterns

# CLEAN CODE:
# - Nombres de clases y métodos: Se utilizan nombres descriptivos y claros (e.g., `Administrador`, `crear_usuario`).
# - Principio de Responsabilidad Única (SRP): La clase `Administrador` se encarga exclusivamente de las operaciones de administración.
# - Tipado estático: Se utiliza `typing` para mejorar la legibilidad y prevenir errores.
# - DRY (Don't Repeat Yourself): Se evita la duplicación de código, como la verificación de roles.
# - Consistencia: El estilo de codificación es consistente en toda la clase.

class Administrador:
    def __init__(self, id_admin: int, username: str, email: str, password: str, rol: int):
        # CLEAN CODE: El constructor es simple y solo asigna valores.
        self.id_admin = id_admin
        self.username = username
        self.email = email
        self.password = password
        self.rol = rol

    # --- Métodos CRUD para Usuario ---

    async def crear_usuario(self, session: AsyncSession, datos: Dict[str, Any]) -> Usuario:
        # CLEAN CODE: El nombre del método es un verbo que describe su acción.
        # CLEAN CODE: Fail-Fast: La validación de rol se hace al principio.
        if self.rol != 0:
            raise PermissionError("Acceso denegado. Se requiere rol de administrador.")
        
        datos.setdefault("mes_suscripcion", 0)
        # The database should handle the ID generation. We use RETURNING to get the new ID.
        query = text(
            """
            INSERT INTO usuario (rol, username, email_usuario, password, activo, mes_suscripcion) 
            VALUES (:rol, :username, :email_usuario, :password, :activo, :mes_suscripcion)
            RETURNING id_usuario
            """
        )
        result = await session.execute(query, datos)
        new_id = result.scalar_one()
        await session.commit()
        
        datos["id_usuario"] = new_id
        return Usuario(**datos)

    async def consultar_usuario(self, session: AsyncSession, id_usuario: int) -> Optional[Usuario]:
        # CLEAN CODE: El nombre del método es claro y conciso.
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return None
        
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
        # CLEAN CODE: El método tiene una única responsabilidad: actualizar un usuario.
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return
            
        sets = [f"{k} = :{k}" for k, v in campos.items()]
        if not sets:
            return
            
        query = text(f"UPDATE usuario SET {', '.join(sets)} WHERE id_usuario = :id")
        params = {"id": id_usuario, **campos}
        await session.execute(query, params)
        await session.commit()

    async def eliminar_usuario(self, session: AsyncSession, id_usuario: int) -> bool:
        # CLEAN CODE: La lógica de negocio (crear memento) está separada de la lógica de base de datos.
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return False
            
        # Memento: Guardar el estado del usuario antes de eliminarlo.
        if not await DesignPatterns.crear_memento_usuario(session, id_usuario):
            await session.rollback()
            print(f"No se pudo crear el memento. La eliminación del usuario {id_usuario} ha sido cancelada.")
            return False

        # Proceder con la eliminación.
        query = text("DELETE FROM usuario WHERE id_usuario = :id")
        try:
            await session.execute(query, {"id": id_usuario})
            await session.commit()
            print(f"Usuario {id_usuario} eliminado correctamente.")
            return True
        except Exception as e:
            await session.rollback()
            print(f"Error al eliminar el usuario {id_usuario}: {e}")
            return False

    async def restaurar_usuario(self, session: AsyncSession, id_usuario: int) -> bool:
        # CLEAN CODE: Delega la lógica de restauración al patrón de diseño.
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return False
        
        return await DesignPatterns.restaurar_usuario_desde_memento(session, id_usuario)

    async def gestionar_estado_usuario(self, session: AsyncSession, id_usuario: int, activo: bool) -> None:
        # CLEAN CODE: El nombre del método es específico y claro.
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return
            
        query = text("UPDATE usuario SET activo = :activo WHERE id_usuario = :id")
        await session.execute(query, {"id": id_usuario, "activo": activo})
        await session.commit()

    # --- Métodos CRUD para Libro ---

    async def crear_libro(self, session: AsyncSession, datos: Dict[str, Any]) -> Libro:
        if self.rol != 0:
            raise PermissionError("Acceso denegado. Se requiere rol de administrador.")
            
        datos.setdefault("sinopsis", "")
        query = text(
            "INSERT INTO libro (id_libro, titulo, autor, categoria, anio_publicacion, sinopsis) "
            "VALUES (:id_libro, :titulo, :autor, :categoria, :anio_publicacion, :sinopsis)"
        )
        await session.execute(query, datos)
        await session.commit()
        return Libro(**datos)

    async def consultar_libro(self, session: AsyncSession, id_libro: int) -> Optional[Libro]:
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return None
            
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
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return
            
        sets = [f"{k} = :{k}" for k, v in campos.items()]
        if not sets:
            return
            
        query = text(f"UPDATE libro SET {', '.join(sets)} WHERE id_libro = :id")
        params = {"id": id_libro, **campos}
        await session.execute(query, params)
        await session.commit()

    async def eliminar_libro(self, session: AsyncSession, id_libro: int) -> None:
        if self.rol != 0:
            print("Acceso denegado. Se requiere rol de administrador.")
            return
            
        query = text("DELETE FROM libro WHERE id_libro = :id")
        await session.execute(query, {"id": id_libro})
        await session.commit()
