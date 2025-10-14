from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession

from app import usuario
from database.connection_db import get_session
from app.usuario import Usuario
from app.gratuito import Gratuito
from app.premium import UsuarioPago
from app.administrador import Administrador
from app.libro import Libro
from app.review import Review
from app.suscripcion import Suscripcion
from datetime import date, timedelta

app = FastAPI(
    title="Modelo de Biblioteca Digital con Acceso Diferenciado",
    description="API que simula el manejo de una biblioteca digital",
    version="La mejor hasta la fecha"
)

# ---------------------- Sistema ----------------------

@app.get("/", response_class=HTMLResponse, tags=["Sistema"])
async def root():
    return "<h1>Biblioteca Digital</h1><p>Bienvenido</p>"

# ---------------------- Usuario ----------------------
# Orden: iniciar_sesion, cerrar_sesion, buscar_libro, cambiar_username, cambiar_contrasena

@app.post("/usuario/iniciarSesion", tags=["Usuario"])
async def usuario_iniciar_sesion(username: str, password: str, session: AsyncSession = Depends(get_session)):
    u = Usuario(id_usuario=0, rol=1, username=username, email_usuario="", password=password, activo=True)
    info = await u.iniciar_sesion(session)
    if not info.get("autenticado"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=info.get("mensaje"))
    return info

@app.post("/usuario/cerrarSesion", tags=["Usuario"])
async def usuario_cerrar_sesion():
    # Lógica mínima, delegada al método si existiera estado persistente
    u = Usuario(0, 1, "", "", "", True)
    await u.cerrar_sesion()
    return {"mensaje": "Sesión cerrada"}

@app.get("/usuario/buscarLibro", tags=["Usuario"])
async def usuario_buscar_libro(
    titulo: Optional[str] = None,
    autor: Optional[str] = None,
    categoria: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    u = Usuario(0, 1, "", "", "", True)
    libro = await u.buscar_libro(session, titulo=titulo, autor=autor, categoria=categoria)
    return {"resultado": libro.__dict__ if libro else None, "descripcion": libro.obtener_descripción() if libro else None}

@app.post("/usuario/cambiarUsername", tags=["Usuario"])
async def usuario_cambiar_username(nuevo_username: str):
    u = Usuario(0, 1, "actual", "", "pwd", True)
    u.cambiar_username(nuevo_username)
    return {"username": u.username}

@app.post("/usuario/cambiarContrasena", tags=["Usuario"])
async def usuario_cambiar_contrasena(nueva_contrasena: str):
    u = Usuario(0, 1, "actual", "", "pwd", True)
    u.cambiar_contrasena(nueva_contrasena)
    return {"contrasena_actualizada": True}

# ---------------------- Gratuito ----------------------
# Orden: leer_fragmento_libro, pasar_a_premium

@app.get("/gratuito/leerFragmentoLibro/{id_libro}", tags=["Gratuito"])
async def gratuito_leer_fragmento_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    g = Gratuito(id_usuario=0, rol=1, username="guest", email_usuario="guest@example.com", password="")
    return await g.leer_fragmento_libro(session, id_libro)

# ---------------------- UsuarioPago (Premium) ----------------------
# Orden: leer_libro_completo, renovar_suscripcion, cancelar_suscripcion

@app.get("/usuarioPago/leerLibroCompleto/{id_libro}", tags=["UsuarioPago"])
async def premium_leer_libro_completo(id_libro: int, session: AsyncSession = Depends(get_session)):
    p = UsuarioPago(id_usuario=0, username="premium", email_usuario="premium@example.com", password="", tipo_suscripcion=1)
    return await p.leer_libro_completo(session, id_libro)

# En endpoints de Administrador, la lógica interna ya usa las tablas 'usuario' y 'libro' por los cambios de la clase.

@app.post("/administrador/crearUsuario", tags=["Administrador"])
async def admin_crear_usuario(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    u = await admin.crear_usuario(session, datos)
    return {"usuario": {
        "id_usuario": u.id_usuario, "rol": u.rol, "username": u.username,
        "email_usuario": u.email_usuario, "activo": u.activo
    }}

@app.get("/administrador/consultarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_consultar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    u = await admin.consultar_usuario(session, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id_usuario": u.id_usuario, "rol": u.rol, "username": u.username, "email_usuario": u.email_usuario, "activo": u.activo}

@app.patch("/administrador/actualizarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_actualizar_usuario(id_usuario: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.actualizar_usuario(session, id_usuario, campos)
    return {"actualizado": True}

@app.delete("/administrador/eliminarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_eliminar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.eliminar_usuario(session, id_usuario)
    return {"eliminado": True}

@app.post("/administrador/gestionarEstadoUsuario/{id_usuario}", tags=["Administrador"])
async def admin_gestionar_estado_usuario(id_usuario: int, activo: bool, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.gestionar_estado_usuario(session, id_usuario, activo)
    return {"id_usuario": id_usuario, "activo": activo}

@app.post("/administrador/crearLibro", tags=["Administrador"])
async def admin_crear_libro(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    l = await admin.crear_libro(session, datos)
    return {"libro": l.__dict__}

@app.get("/administrador/consultarLibro/{id_libro}", tags=["Administrador"])
async def admin_consultar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    l = await admin.consultar_libro(session, id_libro)
    if not l:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return l.__dict__

@app.patch("/administrador/actualizarLibro/{id_libro}", tags=["Administrador"])
async def admin_actualizar_libro(id_libro: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.actualizar_libro(session, id_libro, campos)
    return {"actualizado": True}

@app.delete("/administrador/eliminarLibro/{id_libro}", tags=["Administrador"])
async def admin_eliminar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=0, username="admin", email="admin@example.com", password="admin")
    await admin.eliminar_libro(session, id_libro)
    return {"eliminado": True}

# ---------------------- Libro ----------------------
# Orden: obtener_descripción, obtener_promedio_calificaciones, agregar_review, mostrar_reviews

@app.get("/libro/obtenerDescripcion", tags=["Libro"])
async def libro_obtener_descripcion(id_libro: int, titulo: str, autor: str, categoria: str, anio_publicacion: int):
    l = Libro(id_libro, titulo, autor, categoria, anio_publicacion)
    return {"descripcion": l.obtener_descripción()}

@app.get("/libro/obtenerPromedioCalificaciones", tags=["Libro"])
async def libro_obtener_promedio():
    l = Libro(0, "", "", "", 0)
    return {"promedio": l.obtener_promedio_calificaciones(Review.calificaciones_usuarios)}

@app.post("/libro/agregarReview", tags=["Libro"])
async def libro_agregar_review(id_libro: int, usuario_id: int, comentario: str, calificacion: int):
    l = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    r = Review(
        id_review=len(Review.calificaciones_usuarios) + 1,
        usuario_id=usuario_id,
        libro_id=id_libro,
        comentario=comentario,
        calificacion=calificacion
    )
    r.subir_review()
    l = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"mensaje": "Review agregada", "promedio": l.obtener_promedio_calificaciones([])}

@app.get("/libro/mostrarReviews", tags=["Libro"])
async def libro_mostrar_reviews(id_libro: int):
    l = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"reviews": l.mostrar_reviews()}

# ---------------------- Review ----------------------
# Orden: subir_review, eliminar_review

@app.post("/review/subirReview", tags=["Review"])
async def review_subir_review(usuario_id: int, libro_id: int, comentario: str, calificacion: int):
    r = Review(
        id_review=len(Review.calificaciones_usuarios) + 1,
        usuario_id=usuario_id,
        libro_id=libro_id,
        comentario=comentario,
        calificacion=calificacion
    )
    # Delegar la lógica al método del modelo Review
    r.subir_review()
    l = Libro(id_libro=libro_id, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"mensaje": "Review subida", "promedio": l.obtener_promedio_calificaciones([])}

@app.delete("/review/eliminarReview", tags=["Review"])
async def review_eliminar_review():
    r = Review(id_review=0, usuario_id=0, libro_id=0, comentario="", calificacion=0)
    r.eliminar_review()
    return {"mensaje": "Review eliminada"}

# ---------------------- Suscripcion ----------------------
# Orden: activar_suscripcion_premium, ver_estado_suscripcion

@app.post("/suscripcion/activarSuscripcionPremium", tags=["Suscripcion"])
async def suscripcion_activar_premium(id_suscripcion: int, usuario_id: int, tipo_plan: str = "gratuito", tarifa: int = 0):
    hoy = date.today()
    sus = Suscripcion(id_suscripcion=id_suscripcion, usuario_id=usuario_id, tipo_plan=tipo_plan, fecha_inicio=hoy, fecha_fin=hoy, tarifa=tarifa)
    sus.activar_suscripcion_premium()
    return {"estado": sus.ver_estado_suscripcion()}

@app.get("/suscripcion/verEstadoSuscripcion", tags=["Suscripcion"])
async def suscripcion_ver_estado(id_suscripcion: int, usuario_id: int, tipo_plan: str = "premium"):
    hoy = date.today()
    sus = Suscripcion(id_suscripcion=id_suscripcion, usuario_id=usuario_id, tipo_plan=tipo_plan, fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30), tarifa=100)
    return {"estado": sus.ver_estado_suscripcion()}
