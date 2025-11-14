import csv
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional

class Suscripcion(SQLModel, table=True):
    id_suscripcion: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(...)
    mes_inicio: int = Field(...)
    mes_fin: int = Field(...)
    tarifa: int = Field(...)

DATABASE_URL = "postgresql://adminjuan:Juan893966@fastapi-juan-db.postgres.database.azure.com:5432/postgres"
engine = create_engine(DATABASE_URL)

def create_table():
    SQLModel.metadata.create_all(engine)

def insert_suscripciones_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = []

        for row in reader:
            row["id_suscripcion"] = int(row["id_suscripcion"])
            row["usuario_id"] = int(row["usuario_id"])
            row["mes_inicio"] = int(row["mes_inicio"])
            row["mes_fin"] = int(row["mes_fin"])
            row["tarifa"] = int(row["tarifa"])

            suscripcion = Suscripcion(**row)
            entries.append(suscripcion)

        with Session(engine) as session:
            session.add_all(entries)
            session.commit()

if __name__ == "__main__":
    create_table()
    insert_suscripciones_from_csv("suscripciones.csv")
    print("💳 Datos de suscripciones.csv insertados correctamente.")