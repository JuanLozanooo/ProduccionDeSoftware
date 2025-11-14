from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from typing import Optional

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
    def aplicar_decorador_premium(self):
        pass

    def aplicar_decorador_gratuito(self):
        pass

    # ---------- CHAIN OF RESPONSIBILITY ----------
    def manejar_busqueda_libros(self):
        pass

    def manejar_busqueda_usuarios(self):
        pass