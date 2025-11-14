from sqlmodel.ext.asyncio.session import AsyncSession
from app.usuario import Usuario
from app.suscripcion import Suscripcion
from app.libro import Libro

class Gratuito(Usuario):
    def leer_fragmento_libro(self, libro: Libro) -> dict:
        if self.rol not in [0, 1]:
            return {"error": "Acceso denegado."}

        sinopsis = libro.sinopsis
        if not sinopsis:
            fragmento = "Este libro no tiene sinopsis disponible."
        else:
            midpoint = len(sinopsis) // 2
            fragmento = sinopsis[:midpoint] + "... accede a premium para desbloquear el contenido completo."

        return {
            "titulo": libro.titulo,
            "autor": libro.autor,
            "fragmento": fragmento
        }

    async def pasar_a_premium(self, session: AsyncSession, codigo: str) -> str:
        if self.rol != 1:
            return "Esta función es solo para usuarios gratuitos."

        resultado = await Suscripcion.activar_suscripcion_premium(session, self, codigo)
        return resultado
