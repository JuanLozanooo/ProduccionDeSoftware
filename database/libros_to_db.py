import csv
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional

class Libro(SQLModel, table=True):
    id_libro: Optional[int] = Field(default=None, primary_key=True)
    titulo: str = Field(..., min_length=1, max_length=200)
    autor: str = Field(..., min_length=1, max_length=100)
    categoria: str = Field(..., min_length=1, max_length=100)
    anio_publicacion: int = Field(..., ge=0, le=2025)
    sinopsis: str = Field(..., min_length=1)

DATABASE_URL = "postgresql://adminjuan:Juan893966@fastapi-juan-db.postgres.database.azure.com:5432/postgres"
engine = create_engine(DATABASE_URL)

def create_table():
    SQLModel.metadata.drop_all(engine) # Borra todas las tablas
    SQLModel.metadata.create_all(engine)

def insert_books_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = []

        for row in reader:
            row["id_libro"] = int(row["id_libro"])
            row["anio_publicacion"] = int(row["anio_publicacion"])

            libro = Libro(**row)
            entries.append(libro)

        with Session(engine) as session:
            session.add_all(entries)
            session.commit()

if __name__ == "__main__":
    create_table()
    insert_books_from_csv("libros.csv")
    print("📚 Datos de libros.csv insertados correctamente.")
