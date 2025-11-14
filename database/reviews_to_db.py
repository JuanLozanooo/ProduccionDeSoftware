import csv
from sqlmodel import Field, SQLModel, create_engine, Session
from typing import Optional

class Review(SQLModel, table=True):
    id_review: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(...)
    libro_id: int = Field(...)
    comentario: str = Field(..., max_length=500)

DATABASE_URL = "postgresql://adminjuan:Juan893966@fastapi-juan-db.postgres.database.azure.com:5432/postgres"
engine = create_engine(DATABASE_URL)

def create_table():
    SQLModel.metadata.create_all(engine)

def insert_reviews_from_csv(csv_path: str):
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        entries = []

        for row in reader:
            row["id_review"] = int(row["id_review"])
            row["usuario_id"] = int(row["usuario_id"])
            row["libro_id"] = int(row["libro_id"])

            review = Review(**row)
            entries.append(review)

        with Session(engine) as session:
            session.add_all(entries)
            session.commit()

if __name__ == "__main__":
    create_table()
    insert_reviews_from_csv("reviews.csv")
    print("💬 Datos de reviews.csv insertados correctamente.")