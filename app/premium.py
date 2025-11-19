from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from app.usuario import Usuario
from app.libro import Libro

# CLEAN CODE:
# - Herencia (LSP - Liskov Substitution Principle): `UsuarioPago` es un subtipo de `Usuario` y puede ser usado como tal.
# - Nombres Claros: Los nombres de los métodos (`leer_libro_completo`, `cancelar_suscripcion`) son autoexplicativos.
# - SRP: La clase se enfoca en las funcionalidades específicas de un usuario de pago.
# - Cohesión Alta: Los métodos de la clase están estrechamente relacionados con la gestión de un usuario premium.

class UsuarioPago(Usuario):
    def __init__(self, **kwargs):
        # CLEAN CODE: El constructor es flexible y establece el rol correcto, simplificando la creación de instancias.
        kwargs['rol'] = 2  # El rol para UsuarioPago siempre será 2 (Premium).
        super().__init__(**kwargs)

    def leer_libro_completo(self, libro: Libro) -> dict:
        # CLEAN CODE: El método tiene una única responsabilidad: permitir la lectura de un libro completo.
        # CLEAN CODE: Fail-Fast: La validación de rol se realiza al principio del método.
        if self.rol not in [0, 2]:
            return {"error": "Acceso denegado. Función solo para usuarios Premium."}
        
        return {
            "titulo": libro.titulo,
            "autor": libro.autor,
            "contenido": libro.sinopsis  # Se asume que la sinopsis es el contenido completo.
        }

    async def cancelar_suscripcion(self, session: AsyncSession) -> dict:
        # CLEAN CODE: El método es claro y maneja su propia lógica de negocio, incluyendo el manejo de errores.
        if self.rol != 2:
            return {"mensaje": "El usuario no es Premium."}

        query = text("UPDATE usuario SET rol = 1 WHERE id_usuario = :id")
        try:
            await session.execute(query, {"id": self.id_usuario})
            await session.commit()
            self.rol = 1  # CLEAN CODE: Mantiene el estado del objeto consistente.
            return {"mensaje": "Suscripción cancelada. Su rol ha sido cambiado a gratuito."}
        except Exception as e:
            await session.rollback()
            return {"error": f"No se pudo cancelar la suscripción: {e}"}
