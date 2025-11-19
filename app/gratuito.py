from sqlmodel.ext.asyncio.session import AsyncSession
from app.usuario import Usuario
from app.suscripcion import Suscripcion
from app.libro import Libro

# CLEAN CODE:
# - Herencia: La clase `Gratuito` hereda de `Usuario`, lo que promueve la reutilización de código (DRY).
# - Nombres claros: Los nombres de los métodos (`leer_fragmento_libro`, `pasar_a_premium`) son autoexplicativos.
# - SRP: La clase se centra en las funcionalidades específicas de un usuario gratuito.
# - Cohesión: Los métodos de la clase están relacionados y trabajan juntos en el contexto de un usuario gratuito.

class Gratuito(Usuario):
    def leer_fragmento_libro(self, libro: Libro) -> dict:
        # CLEAN CODE: El método tiene una única responsabilidad: leer un fragmento de un libro.
        # CLEAN CODE: Fail-Fast: La validación de rol se realiza al principio.
        if self.rol not in [0, 1]:
            return {"error": "Acceso denegado."}

        sinopsis = libro.sinopsis
        if not sinopsis:
            fragmento = "Este libro no tiene sinopsis disponible."
        else:
            # CLEAN CODE: La lógica para obtener el fragmento es clara y legible.
            midpoint = len(sinopsis) // 2
            fragmento = sinopsis[:midpoint] + "... accede a premium para desbloquear el contenido completo."

        return {
            "titulo": libro.titulo,
            "autor": libro.autor,
            "fragmento": fragmento
        }

    async def pasar_a_premium(self, session: AsyncSession, codigo: str) -> str:
        # CLEAN CODE: Delega la lógica de activación de la suscripción a la clase `Suscripcion` (SRP).
        if self.rol != 1:
            return "Esta función es solo para usuarios gratuitos."

        resultado = await Suscripcion.activar_suscripcion_premium(session, self, codigo)
        return resultado
