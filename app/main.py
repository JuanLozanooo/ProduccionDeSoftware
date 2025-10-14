from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession

from database.connection_db import get_session
from app.usuario import Usuario
from app.gratuito import Gratuito
from app.premium import UsuarioPago
from app.administrador import Administrador
from app.libro import Libro
from app.review import Review
from app.suscripcion import Suscripcion
from datetime import date, timedelta

# Estado global de sesión
usuario_actual: Optional[Usuario] = None

app = FastAPI(
    title="Modelo de Biblioteca Digital con Acceso Diferenciado",
    description="API que simula el manejo de una biblioteca digital",
    version="La mejor hasta la fecha"
)

# Utilidades de autorización basadas en usuario_actual
def require_login():
    if usuario_actual is None:
        raise HTTPException(status_code=401, detail="Debe iniciar sesión")

def require_role(*roles: int):
    require_login()
    if usuario_actual.rol not in roles:
        raise HTTPException(status_code=403, detail="No tiene permisos para esta acción")

# ---------------------- Sistema ----------------------

@app.get("/", response_class=HTMLResponse, tags=["Sistema"])
async def root():
    return "<h1>Biblioteca Digital</h1><p>Bienvenido</p>"

# ---------------------- Usuario ----------------------
# Orden: iniciar_sesion, cerrar_sesion, buscar_libro, cambiar_username, cambiar_contrasena

@app.post("/usuario/iniciarSesion", tags=["Usuario"])
async def usuario_iniciar_sesion(username: str, password: str, session: AsyncSession = Depends(get_session)):
    global usuario_actual
    u = Usuario(id_usuario=0, rol=1, username=username, email_usuario="", password=password, activo=True)
    info = await u.iniciar_sesion(session)
    if not info.get("autenticado"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Su usuario o contraseña son incorrectos.")
    usuario_actual = u
    return {"mensaje": "Sesión iniciada", "usuario": username, "rol": usuario_actual.rol}

@app.post("/usuario/cerrarSesion", tags=["Usuario"])
async def usuario_cerrar_sesion():
    global usuario_actual
    if usuario_actual is None:
        raise HTTPException(status_code=400, detail="No hay sesión activa")
    usuario_actual = None
    return {"mensaje": "Sesión cerrada correctamente"}

@app.get("/usuario/buscarLibro", tags=["Usuario"])
async def usuario_buscar_libro(
    titulo: Optional[str] = None,
    autor: Optional[str] = None,
    categoria: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    require_login()
    libro = await usuario_actual.buscar_libro(session, titulo=titulo, autor=autor, categoria=categoria)
    return {"resultado": libro.__dict__ if libro else None, "descripcion": libro.obtener_descripción() if libro else None}

@app.post("/usuario/cambiarUsername", tags=["Usuario"])
async def usuario_cambiar_username(nuevo_username: str):
    require_login()
    await usuario_actual.cambiar_username(nuevo_username)
    return {"username": usuario_actual.username}

@app.post("/usuario/cambiarContrasena", tags=["Usuario"])
async def usuario_cambiar_contrasena(nueva_contrasena: str):
    require_login()
    await usuario_actual.cambiar_contrasena(nueva_contrasena)
    return {"contrasena_actualizada": True}

# ---------------------- Gratuito ----------------------
# Orden: leer_fragmento_libro, pasar_a_premium

@app.get("/gratuito/leerFragmentoLibro/{id_libro}", tags=["Gratuito"])
async def gratuito_leer_fragmento_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    require_role(1, 0)  # 1=gratuito, 0=admin (admin puede probar cualquier endpoint)
    # Instanciar como Gratuito usando datos de sesión
    g = Gratuito(id_usuario=usuario_actual.id_usuario, rol=usuario_actual.rol, username=usuario_actual.username, email_usuario=usuario_actual.email_usuario, password=usuario_actual.password)
    return await g.leer_fragmento_libro(session, id_libro)

@app.post("/gratuito/pasarAPremium", tags=["Gratuito"])
async def gratuito_pasar_a_premium():
    require_role(1, 0)
    g = Gratuito(id_usuario=usuario_actual.id_usuario, rol=usuario_actual.rol, username=usuario_actual.username, email_usuario=usuario_actual.email_usuario, password=usuario_actual.password)
    return await g.pasar_a_premium()

# ---------------------- UsuarioPago (Premium) ----------------------
# Orden: leer_libro_completo, renovar_suscripcion, cancelar_suscripcion

@app.get("/usuarioPago/leerLibroCompleto/{id_libro}", tags=["UsuarioPago"])
async def premium_leer_libro_completo(id_libro: int, session: AsyncSession = Depends(get_session)):
    require_role(2, 0)  # 2=premium, 0=admin
    p = UsuarioPago(id_usuario=usuario_actual.id_usuario, username=usuario_actual.username, email_usuario=usuario_actual.email_usuario, password=usuario_actual.password, tipo_suscripcion=1, activo=usuario_actual.activo)
    return await p.leer_libro_completo(session, id_libro)

@app.post("/usuarioPago/renovarSuscripcion", tags=["UsuarioPago"])
async def premium_renovar_suscripcion():
    require_role(2, 0)
    p = UsuarioPago(id_usuario=usuario_actual.id_usuario, username=usuario_actual.username, email_usuario=usuario_actual.email_usuario, password=usuario_actual.password, tipo_suscripcion=1, activo=usuario_actual.activo)
    return await p.renovar_suscripcion()

@app.post("/usuarioPago/cancelarSuscripcion", tags=["UsuarioPago"])
async def premium_cancelar_suscripcion():
    require_role(2, 0)
    p = UsuarioPago(id_usuario=usuario_actual.id_usuario, username=usuario_actual.username, email_usuario=usuario_actual.email_usuario, password=usuario_actual.password, tipo_suscripcion=1, activo=usuario_actual.activo)
    return await p.cancelar_suscripcion()

# ---------------------- Administrador ----------------------
# Orden: crear_usuario, consultar_usuario, actualizar_usuario, eliminar_usuario, gestionar_estado_usuario,
#        crear_libro, consultar_libro, actualizar_libro, eliminar_libro

def require_admin():
    require_role(0)

@app.post("/administrador/crearUsuario", tags=["Administrador"])
async def admin_crear_usuario(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    u = await admin.crear_usuario(session, datos)
    return {"usuario": {
        "id_usuario": u.id_usuario, "rol": u.rol, "username": u.username,
        "email_usuario": u.email_usuario, "activo": u.activo
    }}

@app.get("/administrador/consultarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_consultar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    u = await admin.consultar_usuario(session, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id_usuario": u.id_usuario, "rol": u.rol, "username": u.username, "email_usuario": u.email_usuario, "activo": u.activo}

@app.patch("/administrador/actualizarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_actualizar_usuario(id_usuario: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    await admin.actualizar_usuario(session, id_usuario, campos)
    return {"actualizado": True}

@app.delete("/administrador/eliminarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_eliminar_usuario(id_usuario: int, session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    await admin.eliminar_usuario(session, id_usuario)
    return {"eliminado": True}

@app.post("/administrador/gestionarEstadoUsuario/{id_usuario}", tags=["Administrador"])
async def admin_gestionar_estado_usuario(id_usuario: int, activo: bool, session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    await admin.gestionar_estado_usuario(session, id_usuario, activo)
    return {"id_usuario": id_usuario, "activo": activo}

@app.post("/administrador/crearLibro", tags=["Administrador"])
async def admin_crear_libro(datos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    l = await admin.crear_libro(session, datos)
    return {"libro": l.__dict__}

@app.get("/administrador/consultarLibro/{id_libro}", tags=["Administrador"])
async def admin_consultar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    l = await admin.consultar_libro(session, id_libro)
    if not l:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return l.__dict__

@app.patch("/administrador/actualizarLibro/{id_libro}", tags=["Administrador"])
async def admin_actualizar_libro(id_libro: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    await admin.actualizar_libro(session, id_libro, campos)
    return {"actualizado": True}

@app.delete("/administrador/eliminarLibro/{id_libro}", tags=["Administrador"])
async def admin_eliminar_libro(id_libro: int, session: AsyncSession = Depends(get_session)):
    require_admin()
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password)
    await admin.eliminar_libro(session, id_libro)
    return {"eliminado": True}

# ---------------------- Libro ----------------------
# Orden: obtener_descripción, obtener_promedio_calificaciones, agregar_review, mostrar_reviews

@app.get("/libro/obtenerDescripcion", tags=["Libro"])
async def libro_obtener_descripcion(id_libro: int, titulo: str, autor: str, categoria: str, anio_publicacion: int):
    require_login()
    l = Libro(id_libro, titulo, autor, categoria, anio_publicacion)
    return {"descripcion": l.obtener_descripción()}

@app.get("/libro/obtenerPromedioCalificaciones", tags=["Libro"])
async def libro_obtener_promedio(id_libro: int):
    require_login()
    l = Libro(id_libro, "", "", "", 0)
    return {"promedio": l.obtener_promedio_calificaciones([])}

@app.post("/libro/agregarReview", tags=["Libro"])
async def libro_agregar_review(id_libro: int, comentario: str, calificacion: int):
    require_role(2, 0)  # Solo premium o admin pueden reseñar desde este endpoint de libro
    r = Review(
        id_review=len(Review.calificaciones_usuarios) + 1,
        usuario_id=usuario_actual.id_usuario,
        libro_id=id_libro,
        comentario=comentario,
        calificacion=calificacion
    )
    r.subir_review()
    l = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"mensaje": "Review agregada", "promedio": l.obtener_promedio_calificaciones([])}

@app.get("/libro/mostrarReviews", tags=["Libro"])
async def libro_mostrar_reviews(id_libro: int):
    require_login()
    l = Libro(id_libro=id_libro, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"reviews": l.mostrar_reviews()}

# ---------------------- Review ----------------------
# Orden: subir_review, eliminar_review

@app.post("/review/subirReview", tags=["Review"])
async def review_subir_review(libro_id: int, comentario: str, calificacion: int):
    require_role(2, 0)  # premium o admin
    r = Review(
        id_review=len(Review.calificaciones_usuarios) + 1,
        usuario_id=usuario_actual.id_usuario,
        libro_id=libro_id,
        comentario=comentario,
        calificacion=calificacion
    )
    r.subir_review()
    l = Libro(id_libro=libro_id, titulo="", autor="", categoria="", anio_publicacion=0)
    return {"mensaje": "Review subida", "promedio": l.obtener_promedio_calificaciones([])}

@app.delete("/review/eliminarReview", tags=["Review"])
async def review_eliminar_review():
    require_role(2, 0)
    r = Review(id_review=0, usuario_id=usuario_actual.id_usuario, libro_id=0, comentario="", calificacion=0)
    r.eliminar_review()
    return {"mensaje": "Review eliminada"}

# ---------------------- Suscripcion ----------------------
# Orden: activar_suscripcion_premium, ver_estado_suscripcion

@app.post("/suscripcion/activarSuscripcionPremium", tags=["Suscripcion"])
async def suscripcion_activar_premium(id_suscripcion: int):
    require_role(1, 2, 0)  # cualquier usuario logueado puede activar/renovar (simulado)
    hoy = date.today()
    sus = Suscripcion(id_suscripcion=id_suscripcion, usuario_id=usuario_actual.id_usuario, tipo_plan="gratuito", fecha_inicio=hoy, fecha_fin=hoy, tarifa=0)
    sus.activar_suscripcion_premium()
    return {"estado": sus.ver_estado_suscripcion()}

@app.get("/suscripcion/verEstadoSuscripcion", tags=["Suscripcion"])
async def suscripcion_ver_estado():
    require_login()
    hoy = date.today()
    sus = Suscripcion(id_suscripcion=1, usuario_id=usuario_actual.id_usuario, tipo_plan="premium", fecha_inicio=hoy, fecha_fin=hoy + timedelta(days=30), tarifa=100)
    return {"estado": sus.ver_estado_suscripcion()}

# ---------------------- Gratuito/Premium helpers opcionales ----------------------

@app.get("/gratuito/pasarAPremium", tags=["Gratuito"])
async def gratuito_pasar_premium_alias():
    return await gratuito_pasar_a_premium()
