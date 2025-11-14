import csv
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional

class Eliminado(SQLModel, table=True):
    __tablename__ = "eliminado"

    id_usuario: Optional[int] = Field(default=None, primary_key=True)
    rol: int = Field(..., ge=0, le=2)
    username: str = Field(..., min_length=3, max_length=50)
    email_usuario: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=3, max_length=100)
    activo: bool = Field(default=False)
    mes_suscripcion: int = Field(default=0)

DATABASE_URL = "postgresql://adminjuan:Juan893966@fastapi-juan-db.postgres.database.azure.com:5432/postgres"
engine = create_engine(DATABASE_URL)

def create_table():
    SQLModel.metadata.create_all(engine)

def insert_eliminados_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = []

        for row in reader:
            row["id_usuario"] = int(row["id_usuario"])
            row["rol"] = int(row["rol"])
            row["mes_suscripcion"] = int(row["mes_suscripcion"])
            row["activo"] = row["activo"].strip().lower() == "true"

            eliminado = Eliminado(**row)
            entries.append(eliminado)

        with Session(engine) as session:
            session.add_all(entries)
            session.commit()

if __name__ == "__main__":
    create_table()
    insert_eliminados_from_csv("eliminados.csv")
    print("🗑️ Datos de eliminados.csv insertados correctamente.")