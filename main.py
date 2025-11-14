from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from typing import Optional, Dict, Any, Union
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from database.connection_db import get_session, init_db
from fastapi.templating import Jinja2Templates
import os

from app.usuario import Usuario
from app.gratuito import Gratuito
from app.premium import UsuarioPago
from app.administrador import Administrador
from app.libro import Libro
from app.review import Review
from app.suscripcion import Suscripcion

# Estado global de sesión (ADVERTENCIA: No es seguro para producción, usar un sistema de tokens)
usuario_actual: Optional[Usuario] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación y creando tablas si es necesario...")
    await init_db()
    print("Tablas listas.")
    yield
    print("Cerrando aplicación.")

app = FastAPI(
    title="Modelo de Biblioteca Digital",
    description="API que simula el manejo de una biblioteca digital.",
    version="1.0.1",
    lifespan=lifespan
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Dependencias y Utilidades de Autorización ---

def require_login():
    if usuario_actual is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Debe iniciar sesión")

def require_role(*roles: int):
    require_login()
    if usuario_actual.rol not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para esta acción")

async def get_libro_by_id(id_libro: int, session: AsyncSession = Depends(get_session)) -> Libro:
    admin = Administrador(0, "", "", "") # Instancia temporal para acceder al método
    libro = await admin.consultar_libro(session, id_libro)
    if not libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    return libro

# ---------------------- Sistema ----------------------

@app.get("/", response_class=HTMLResponse, tags=["Página Principal"])
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# ---------------------- Usuario ----------------------

@app.post("/usuario/iniciarSesion", tags=["Usuario"])
async def usuario_iniciar_sesion(username: str, password: str, session: AsyncSession = Depends(get_session)):
    global usuario_actual
    # Se crea una instancia temporal para la autenticación
    u = Usuario(id_usuario=0, rol=0, username=username, email_usuario="", password=password)
    info = await u.iniciar_sesion(session)
    if not info.get("autenticado"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Su usuario o contraseña son incorrectos.")
    
    # El objeto 'u' ahora contiene toda la información del usuario desde la BD
    usuario_actual = u
    return {"mensaje": "Sesión iniciada", "usuario": usuario_actual.username, "rol": usuario_actual.rol}

@app.post("/usuario/cerrarSesion", tags=["Usuario"])
async def usuario_cerrar_sesion():
    global usuario_actual
    require_login()
    resultado = await usuario_actual.cerrar_sesion()
    usuario_actual = None
    return resultado

@app.get("/usuario/buscarLibro", tags=["Usuario"])
async def usuario_buscar_libro(
    titulo: Optional[str] = None, autor: Optional[str] = None, categoria: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    require_login()
    libro = await usuario_actual.buscar_libro(session, titulo=titulo, autor=autor, categoria=categoria)
    if not libro:
        return {"resultado": None, "descripcion": "No se encontraron libros con esos criterios."}
    return {"resultado": libro.__dict__, "descripcion": libro.obtener_descripción()}

@app.post("/usuario/cambiarUsername", tags=["Usuario"])
async def usuario_cambiar_username(nuevo_username: str, session: AsyncSession = Depends(get_session)):
    require_login()
    return await usuario_actual.cambiar_username(session, nuevo_username)

@app.post("/usuario/cambiarContrasena", tags=["Usuario"])
async def usuario_cambiar_contrasena(nueva_contrasena: str, session: AsyncSession = Depends(get_session)):
    require_login()
    return await usuario_actual.cambiar_contrasena(session, nueva_contrasena)

# ---------------------- Gratuito ----------------------

@app.get("/gratuito/leerFragmentoLibro/{id_libro}", tags=["Gratuito"])
async def gratuito_leer_fragmento_libro(libro: Libro = Depends(get_libro_by_id)):
    require_role(0, 1)
    g = Gratuito(**usuario_actual.__dict__)
    return g.leer_fragmento_libro(libro)

@app.post("/gratuito/pasarAPremium", tags=["Gratuito"])
async def gratuito_pasar_a_premium(codigo: str, session: AsyncSession = Depends(get_session)):
    require_role(1)
    g = Gratuito(**usuario_actual.__dict__)
    return await g.pasar_a_premium(session, codigo)

# ---------------------- UsuarioPago (Premium) ----------------------

@app.get("/usuarioPago/leerLibroCompleto/{id_libro}", tags=["UsuarioPago"])
async def premium_leer_libro_completo(libro: Libro = Depends(get_libro_by_id)):
    require_role(0, 2)
    p = UsuarioPago(**usuario_actual.__dict__)
    return p.leer_libro_completo(libro)

@app.post("/usuarioPago/cancelarSuscripcion", tags=["UsuarioPago"])
async def premium_cancelar_suscripcion(session: AsyncSession = Depends(get_session)):
    require_role(2)
    p = UsuarioPago(**usuario_actual.__dict__)
    resultado = await p.cancelar_suscripcion(session)
    # Actualizar el estado del usuario en la sesión global
    if "error" not in resultado:
        usuario_actual.rol = 1
    return resultado

# ---------------------- Review ----------------------

@app.post("/review/subirReview/{id_libro}", tags=["Review"])
async def review_subir_review(comentario: str, libro: Libro = Depends(get_libro_by_id), session: AsyncSession = Depends(get_session)):
    require_login()
    r = Review(comentario=comentario)
    await r.subir_review(session, usuario_actual, libro)
    return {"mensaje": "Review subida correctamente.", "review_id": r.id_review}

# ---------------------- Libro ----------------------

@app.get("/libro/mostrarReviews/{id_libro}", tags=["Libro"])
async def libro_mostrar_reviews(libro: Libro = Depends(get_libro_by_id), session: AsyncSession = Depends(get_session)):
    require_login()
    reviews = await libro.mostrar_reviews(session)
    return {"reviews": reviews}

# ---------------------- Suscripcion ----------------------

@app.post("/suscripcion/activarSuscripcionPremium", tags=["Suscripcion"])
async def suscripcion_activar_premium(codigo: str, session: AsyncSession = Depends(get_session)):
    require_role(1) # Solo usuarios gratuitos pueden activar una nueva suscripción
    resultado = await Suscripcion.activar_suscripcion_premium(session, usuario_actual, codigo)
    # Actualizar el estado del usuario en la sesión global
    if "Error" not in resultado:
        usuario_actual.rol = 2
    return {"estado": resultado}

@app.get("/suscripcion/verEstadoSuscripcion", tags=["Suscripcion"])
async def suscripcion_ver_estado(session: AsyncSession = Depends(get_session)) -> Union[Dict[str, Any], str]:
    require_login()
    return await Suscripcion.ver_estado_suscripcion(session, usuario_actual)

# ---------------------- Administrador ----------------------

def get_admin() -> Administrador:
    require_role(0)
    return Administrador(
        id_admin=usuario_actual.id_usuario,
        username=usuario_actual.username,
        email=usuario_actual.email_usuario,
        password=usuario_actual.password
    )

@app.post("/administrador/crearUsuario", tags=["Administrador"])
async def admin_crear_usuario(datos: Dict[str, Any], admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    u = await admin.crear_usuario(session, datos)
    return u.__dict__

@app.get("/administrador/consultarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_consultar_usuario(id_usuario: int, admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    u = await admin.consultar_usuario(session, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u.__dict__

@app.patch("/administrador/actualizarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_actualizar_usuario(id_usuario: int, campos: Dict[str, Any], admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    await admin.actualizar_usuario(session, id_usuario, campos)
    return {"mensaje": "Usuario actualizado correctamente"}

@app.delete("/administrador/eliminarUsuario/{id_usuario}", tags=["Administrador"])
async def admin_eliminar_usuario(id_usuario: int, admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    await admin.eliminar_usuario(session, id_usuario)
    return {"mensaje": "Usuario eliminado correctamente"}

@app.post("/administrador/gestionarEstadoUsuario/{id_usuario}", tags=["Administrador"])
async def admin_gestionar_estado_usuario(id_usuario: int, activo: bool, admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    await admin.gestionar_estado_usuario(session, id_usuario, activo)
    return {"id_usuario": id_usuario, "activo": activo}

@app.post("/administrador/crearLibro", tags=["Administrador"])
async def admin_crear_libro(datos: Dict[str, Any], admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    l = await admin.crear_libro(session, datos)
    return l.__dict__

@app.get("/administrador/consultarLibro/{id_libro}", tags=["Administrador"])
async def admin_consultar_libro(id_libro: int, admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    l = await admin.consultar_libro(session, id_libro)
    if not l:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return l.__dict__

@app.patch("/administrador/actualizarLibro/{id_libro}", tags=["Administrador"])
async def admin_actualizar_libro(id_libro: int, campos: Dict[str, Any], admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    await admin.actualizar_libro(session, id_libro, campos)
    return {"mensaje": "Libro actualizado correctamente"}

@app.delete("/administrador/eliminarLibro/{id_libro}", tags=["Administrador"])
async def admin_eliminar_libro(id_libro: int, admin: Administrador = Depends(get_admin), session: AsyncSession = Depends(get_session)):
    await admin.eliminar_libro(session, id_libro)
    return {"mensaje": "Libro eliminado correctamente"}
