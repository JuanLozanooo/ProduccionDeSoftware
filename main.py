from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, Dict, Any, Union
from sqlmodel.ext.asyncio.session import AsyncSession
from contextlib import asynccontextmanager
from database.connection_db import get_session, init_db
from fastapi.templating import Jinja2Templates
import os
from functools import wraps

from app.usuario import Usuario
from app.gratuito import Gratuito
from app.premium import UsuarioPago
from app.administrador import Administrador
from app.libro import Libro
from app.review import Review
from app.suscripcion import Suscripcion

# --- Authentication and Authorization ---
usuario_actual: Optional[Usuario] = None

def role_required(allowed_roles: list[int]):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            if usuario_actual is None:
                return templates.TemplateResponse("login.html", {"request": request, "error": "Debe iniciar sesión"})
            if usuario_actual.rol not in allowed_roles:
                return templates.TemplateResponse("access_denied.html", {"request": request})
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

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

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if usuario_actual is None:
        return templates.TemplateResponse("login.html", {"request": request})
    return templates.TemplateResponse("home.html", {"request": request, "usuario": usuario_actual})

@app.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), session: AsyncSession = Depends(get_session)):
    global usuario_actual
    u = Usuario(id_usuario=0, rol=0, username=username, email_usuario="", password=password)
    info = await u.iniciar_sesion(session)
    if not info.get("autenticado"):
        return templates.TemplateResponse("login.html", {"request": request, "error": info.get("mensaje")})
    
    usuario_actual = u
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout(request: Request):
    global usuario_actual
    usuario_actual = None
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# --- Administrator Views ---

@app.get("/admin/crear_usuario_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_crear_usuario(request: Request):
    return templates.TemplateResponse("admin/crear_usuario.html", {"request": request})

@app.get("/admin/consultar_usuario_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_consultar_usuario(request: Request):
    return templates.TemplateResponse("admin/consultar_usuario.html", {"request": request})

@app.get("/admin/actualizar_usuario_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_actualizar_usuario(request: Request):
    return templates.TemplateResponse("admin/actualizar_usuario.html", {"request": request})

@app.get("/admin/eliminar_usuario_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_eliminar_usuario(request: Request):
    return templates.TemplateResponse("admin/eliminar_usuario.html", {"request": request})

@app.get("/admin/gestionar_estado_usuario_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_gestionar_estado_usuario(request: Request):
    return templates.TemplateResponse("admin/gestionar_estado_usuario.html", {"request": request})

@app.get("/admin/crear_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_crear_libro(request: Request):
    return templates.TemplateResponse("admin/crear_libro.html", {"request": request})

@app.get("/admin/consultar_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_consultar_libro(request: Request):
    return templates.TemplateResponse("admin/consultar_libro.html", {"request": request})

@app.get("/admin/actualizar_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_actualizar_libro(request: Request):
    return templates.TemplateResponse("admin/actualizar_libro.html", {"request": request})

@app.get("/admin/eliminar_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0])
async def form_eliminar_libro(request: Request):
    return templates.TemplateResponse("admin/eliminar_libro.html", {"request": request})

# --- User Views ---
@app.get("/user/buscar_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0, 1, 2])
async def form_buscar_libro(request: Request):
    return templates.TemplateResponse("user/buscar_libro.html", {"request": request})

@app.get("/user/cambiar_username_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0, 1, 2])
async def form_cambiar_username(request: Request):
    return templates.TemplateResponse("user/cambiar_username.html", {"request": request})

@app.get("/user/cambiar_contrasena_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0, 1, 2])
async def form_cambiar_contrasena(request: Request):
    return templates.TemplateResponse("user/cambiar_contrasena.html", {"request": request})

# --- Gratuito Views ---
@app.get("/gratuito/leer_fragmento_libro_form", response_class=HTMLResponse)
@role_required(allowed_roles=[1])
async def form_leer_fragmento_libro(request: Request):
    return templates.TemplateResponse("gratuito/leer_fragmento_libro.html", {"request": request})

@app.get("/gratuito/pasar_a_premium_form", response_class=HTMLResponse)
@role_required(allowed_roles=[1])
async def form_pasar_a_premium(request: Request):
    return templates.TemplateResponse("gratuito/pasar_a_premium.html", {"request": request})

# --- Premium Views ---
@app.get("/premium/leer_libro_completo_form", response_class=HTMLResponse)
@role_required(allowed_roles=[2])
async def form_leer_libro_completo(request: Request):
    return templates.TemplateResponse("premium/leer_libro_completo.html", {"request": request})

@app.get("/premium/cancelar_suscripcion_form", response_class=HTMLResponse)
@role_required(allowed_roles=[2])
async def form_cancelar_suscripcion(request: Request):
    return templates.TemplateResponse("premium/cancelar_suscripcion.html", {"request": request})

# --- Review Views ---
@app.get("/review/subir_review_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0, 1, 2])
async def form_subir_review(request: Request):
    return templates.TemplateResponse("review/subir_review.html", {"request": request})

# --- Suscripcion Views ---
@app.get("/suscripcion/activar_suscripcion_premium_form", response_class=HTMLResponse)
@role_required(allowed_roles=[1])
async def form_activar_suscripcion_premium(request: Request):
    return templates.TemplateResponse("suscripcion/activar_suscripcion_premium.html", {"request": request})

@app.get("/suscripcion/ver_estado_suscripcion_form", response_class=HTMLResponse)
@role_required(allowed_roles=[0, 1, 2])
async def form_ver_estado_suscripcion(request: Request):
    return templates.TemplateResponse("suscripcion/ver_estado_suscripcion.html", {"request": request})
    
# --- API Endpoints (for AJAX calls from templates) ---

@app.post("/api/admin/crear_usuario", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_crear_usuario(request: Request, session: AsyncSession = Depends(get_session), datos: Dict[str, Any] = None):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    # Logic to create user from form data
    # ...
    return {"message": "Usuario creado"}

@app.get("/api/admin/consultar_usuario/{id_usuario}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_consultar_usuario(request: Request, id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    u = await admin.consultar_usuario(session, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u.__dict__

@app.patch("/api/admin/actualizar_usuario/{id_usuario}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_actualizar_usuario(request: Request, id_usuario: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    await admin.actualizar_usuario(session, id_usuario, campos)
    return {"mensaje": "Usuario actualizado correctamente"}

@app.delete("/api/admin/eliminar_usuario/{id_usuario}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_eliminar_usuario(request: Request, id_usuario: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    await admin.eliminar_usuario(session, id_usuario)
    return {"mensaje": "Usuario eliminado correctamente"}

@app.post("/api/admin/gestionar_estado_usuario/{id_usuario}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_gestionar_estado_usuario(request: Request, id_usuario: int, activo: bool, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    await admin.gestionar_estado_usuario(session, id_usuario, activo)
    return {"id_usuario": id_usuario, "activo": activo}

@app.post("/api/admin/crear_libro", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_crear_libro(request: Request, session: AsyncSession = Depends(get_session), datos: Dict[str, Any] = None):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    # Logic to create book from form data
    # ...
    return {"message": "Libro creado"}

@app.get("/api/admin/consultar_libro/{id_libro}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_consultar_libro(request: Request, id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    l = await admin.consultar_libro(session, id_libro)
    if not l:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return l.__dict__

@app.patch("/api/admin/actualizar_libro/{id_libro}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_actualizar_libro(request: Request, id_libro: int, campos: Dict[str, Any], session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    await admin.actualizar_libro(session, id_libro, campos)
    return {"mensaje": "Libro actualizado correctamente"}

@app.delete("/api/admin/eliminar_libro/{id_libro}", tags=["Administrador"])
@role_required(allowed_roles=[0])
async def api_eliminar_libro(request: Request, id_libro: int, session: AsyncSession = Depends(get_session)):
    admin = Administrador(id_admin=usuario_actual.id_usuario, username=usuario_actual.username, email=usuario_actual.email_usuario, password=usuario_actual.password, rol=usuario_actual.rol)
    await admin.eliminar_libro(session, id_libro)
    return {"mensaje": "Libro eliminado correctamente"}

@app.post("/api/user/buscar_libro", tags=["Usuario"])
@role_required(allowed_roles=[0, 1, 2])
async def api_buscar_libro(request: Request, session: AsyncSession = Depends(get_session), search_term: str = Form(...)):
    libro = await usuario_actual.buscar_libro(session, search_term)
    if not libro:
        return {"resultado": "No se encontraron libros."}
    return {"resultado": libro.obtener_descripción()}

@app.post("/api/user/cambiar_username", tags=["Usuario"])
@role_required(allowed_roles=[0, 1, 2])
async def api_cambiar_username(request: Request, nuevo_username: str = Form(...), session: AsyncSession = Depends(get_session)):
    return await usuario_actual.cambiar_username(session, nuevo_username)

@app.post("/api/user/cambiar_contrasena", tags=["Usuario"])
@role_required(allowed_roles=[0, 1, 2])
async def api_cambiar_contrasena(request: Request, nueva_contrasena: str = Form(...), session: AsyncSession = Depends(get_session)):
    return await usuario_actual.cambiar_contrasena(session, nueva_contrasena)

@app.get("/api/gratuito/leer_fragmento_libro/{id_libro}", tags=["Gratuito"])
@role_required(allowed_roles=[1])
async def api_leer_fragmento_libro(request: Request, id_libro: int, session: AsyncSession = Depends(get_session)):
    g = Gratuito(**usuario_actual.__dict__)
    libro = await Administrador(0,"","","",0).consultar_libro(session, id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return g.leer_fragmento_libro(libro)

@app.post("/api/gratuito/pasar_a_premium", tags=["Gratuito"])
@role_required(allowed_roles=[1])
async def api_pasar_a_premium(request: Request, codigo: str = Form(...), session: AsyncSession = Depends(get_session)):
    g = Gratuito(**usuario_actual.__dict__)
    return await g.pasar_a_premium(session, codigo)

@app.get("/api/premium/leer_libro_completo/{id_libro}", tags=["Premium"])
@role_required(allowed_roles=[2])
async def api_leer_libro_completo(request: Request, id_libro: int, session: AsyncSession = Depends(get_session)):
    p = UsuarioPago(**usuario_actual.__dict__)
    libro = await Administrador(0,"","","",0).consultar_libro(session, id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return p.leer_libro_completo(libro)

@app.post("/api/premium/cancelar_suscripcion", tags=["Premium"])
@role_required(allowed_roles=[2])
async def api_cancelar_suscripcion(request: Request, session: AsyncSession = Depends(get_session)):
    p = UsuarioPago(**usuario_actual.__dict__)
    return await p.cancelar_suscripcion(session)

@app.post("/api/review/subir_review/{id_libro}", tags=["Review"])
@role_required(allowed_roles=[0, 1, 2])
async def api_subir_review(request: Request, id_libro: int, comentario: str = Form(...), session: AsyncSession = Depends(get_session)):
    r = Review(comentario=comentario)
    libro = await Administrador(0,"","","",0).consultar_libro(session, id_libro)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    await r.subir_review(session, usuario_actual, libro)
    return {"mensaje": "Review subida correctamente."}

@app.post("/api/suscripcion/activar_suscripcion_premium", tags=["Suscripcion"])
@role_required(allowed_roles=[1])
async def api_activar_suscripcion_premium(request: Request, codigo: str = Form(...), session: AsyncSession = Depends(get_session)):
    return await Suscripcion.activar_suscripcion_premium(session, usuario_actual, codigo)

@app.get("/api/suscripcion/ver_estado_suscripcion", tags=["Suscripcion"])
@role_required(allowed_roles=[0, 1, 2])
async def api_ver_estado_suscripcion(request: Request, session: AsyncSession = Depends(get_session)):
    return await Suscripcion.ver_estado_suscripcion(session, usuario_actual)
