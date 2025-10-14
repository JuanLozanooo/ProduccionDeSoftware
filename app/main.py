from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from typing import List, Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from database.connection_db import get_session
from app.usuario import Usuario
from app.gratuito import Gratuito
from app.premium import UsuarioPago
from app.administrador import Administrador
from app.libro import Libro
from app.review import Review
from app.suscripcion import Suscripcion
import os

app = FastAPI(
    title="Modelo de Biblioteca Digital con Acceso Diferenciado",
    description="API que simula el manejo de una biblioteca digital",
    version="La mejor hasta la fecha"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return "<h1>Biblioteca Digital</h1><p>Bienvenido</p>"

# Autenticación / Sesión
@app.post("/login")
async def login(email: str, password: str, session: AsyncSession = Depends(get_session)):
    user_tmp = Usuario(id_usuario=0, rol=1, username="", email_usuario=email, password=password, activo=True)
    info = await user_tmp.iniciar_sesion(session)
    if not info.get("autenticado"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=info.get("mensaje"))
    return info

@app.post("/logout")
async def logout():
    return {"mensaje": "Sesión cerrada (simulada)."}

# Usuarios - Admin
@app.post("/admin/usuarios")
async def crear_usuario(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    usuario = await admin.crear_usuario(session, datos)
    return {"creado": True, "usuario": {
        "id_usuario": usuario.id_usuario,
        "rol": usuario.rol,
        "username": usuario.username,
        "email_usuario": usuario.email_usuario,
        "activo": usuario.activo
    }}

@app.get("/admin/usuarios/{id_usuario}")
async def consultar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    usuario = await admin.consultar_usuario(session, id_usuario)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id_usuario": usuario.id_usuario,
        "rol": usuario.rol,
        "username": usuario.username,
        "email_usuario": usuario.email_usuario,
        "activo": usuario.activo
    }

@app.patch("/admin/usuarios/{id_usuario}")
async def actualizar_usuario(id_usuario: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.actualizar_usuario(session, id_usuario, campos)
    return {"actualizado": True}

@app.delete("/admin/usuarios/{id_usuario}")
async def eliminar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.eliminar_usuario(session, id_usuario)
    return {"eliminado": True}

@app.post("/admin/usuarios/{id_usuario}/estado")
async def gestionar_estado_usuario(id_usuario: int, activo: bool, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.gestionar_estado_usuario(session, id_usuario, activo)
    return {"id_usuario": id_usuario, "activo": activo}

# Libros - Admin
@app.post("/admin/libros")
async def crear_libro(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    libro = await admin.crear_libro(session, datos)
    return {"creado": True, "libro": libro.__dict__}

@app.get("/admin/libros/{id_libro}")
async def consultar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    libro = await admin.consultar_libro(session, id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro.__dict__

@app.patch("/admin/libros/{id_libro}")
async def actualizar_libro(id_libro: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.actualizar_libro(session, id_libro, campos)
    return {"actualizado": True}

@app.delete("/admin/libros/{id_libro}")
async def eliminar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.eliminar_libro(session, id_libro)
    return {"eliminado": True}

# Búsqueda de libros (Usuarios)
@app.get("/libros/buscar")
async def buscar_libro(
    titulo: Optional[str] = None,
    autor: Optional[str] = None,
    categoria: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    user = Usuario(id_usuario=0, rol=1, username="", email_usuario="", password="")
    libro = await user.buscar_libro(session, titulo=titulo, autor=autor, categoria=categoria)
    if not libro:
        return {"resultado": None}
    return {"resultado": libro.__dict__, "descripcion": libro.obtener_descripción()}

# Funciones Gratuito
@app.get("/gratuito/libros/{id_libro}/fragmento")
async def leer_fragmento(id_libro: int, session: AsyncSession = Depends(get_session)):
    user = Gratuito(id_usuario=0, rol=1, username="guest", email_usuario="guest@example.com", password="")
    data = await user.leer_fragmento_libro(session, id_libro)
    return data

# Funciones Premium
@app.get("/premium/libros/{id_libro}/leer")
async def leer_completo(id_libro: int, session: AsyncSession = Depends(get_session)):
    user = UsuarioPago(id_usuario=0, username="premium", email_usuario="premium@example.com", password="", tipo_suscripcion=1)
    data = await user.leer_libro_completo(session, id_libro)
    return data

# Reviews en memoria
@app.post("/libros/{id_libro}/reviews")
async def agregar_review(id_libro: int, usuario_id: int, comentario: str, calificacion: int):
    review = Review(
        id_review=len(Review.calificaciones_usuarios) + 1,
        usuario_id=usuario_id,
        libro_id=id_libro,
        comentario=comentario,
        calificacion=calificacion
    )
    libro_tmp = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    libro_tmp.agregar_review(review)
    promedio = libro_tmp.obtener_promedio_calificaciones(Review.calificaciones_usuarios)
    return {"mensaje": "Review agregada", "promedio": promedio}

@app.get("/libros/{id_libro}/reviews")
async def ver_reviews(id_libro: int):
    libro_tmp = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"reviews": libro_tmp.mostrar_reviews(), "promedio": libro_tmp.obtener_promedio_calificaciones(Review.calificaciones_usuarios)}

# Suscripciones (simuladas en memoria)
@app.post("/usuarios/{id_usuario}/suscripcion/activar")
async def activar_suscripcion(id_usuario: int):
    sus = Suscripcion(id_suscripcion=1, usuario_id=id_usuario, tipo_plan="gratuito", fecha_inicio=os.getenv("TODAY") or None, fecha_fin=os.getenv("TODAY") or None, tarifa=0)
    sus.activar_suscripcion_premium()
    return {"estado": sus.ver_estado_suscripcion()}

@app.get("/usuarios/{id_usuario}/suscripcion")
async def estado_suscripcion(id_usuario: int):
    # Para demo, devolvemos un estado ficticio
    sus = Suscripcion(id_suscripcion=1, usuario_id=id_usuario, tipo_plan="premium", fecha_inicio=suscripcion_hoy()[0], fecha_fin=suscripcion_hoy()[1], tarifa=100)
    return {"estado": sus.ver_estado_suscripcion()}

def suscripcion_hoy():
    from datetime import date, timedelta
    hoy = date.today()
    return hoy, hoy + timedelta(days=30)
