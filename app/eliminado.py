from typing import Optional
from sqlmodel import Field, SQLModel

class Eliminado(SQLModel, table=True):
    """
    Representa un 'memento' de un usuario que ha sido eliminado.
    Esta tabla almacena el estado de un usuario en el momento de su eliminación.
    """
    __tablename__ = "eliminado"

    id_usuario: int = Field(primary_key=True)
    rol: int
    username: str
    email_usuario: str
    password: str
    activo: bool
    mes_suscripcion: Optional[int] = None
