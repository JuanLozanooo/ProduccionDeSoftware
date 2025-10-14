from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.usuario import Usuario

class Gratuito(Usuario):
    async def leer_fragmento_libro(self, session: AsyncSession, id_libro: int) -> dict:
        """
        Devuelve un fragmento simulado del libro (por ejemplo, las primeras líneas de la descripción).
        """
        query = text("SELECT id_libro, titulo, autor, categoria, anio_publicacion FROM libro WHERE id_libro = :id")
        result = await session.execute(query, {"id": id_libro})
        row = result.first()
        if not row:
            return {"mensaje": "Libro no encontrado"}
        fragmento = f"{row.titulo} - {row.autor} ({row.anio_publicacion}): Inicio de muestra..."
        return {"id_libro": row.id_libro, "fragmento": fragmento}

    async def pasar_a_premium(self) -> dict:
        # Lógica de cambio de plan se manejaría en endpoints; aquí devolvemos intención.
        return {"mensaje": "Para pasar a premium, renueva o crea una suscripción."}
