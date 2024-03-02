import os
import logging
from dotenv import load_dotenv

from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

# Usando logging para mostrar mensajes en la consola.
# Todos amamos print('XXXXX') pero logging es la manera correcta/profesional
# de hacerlo :)
logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger(__name__)

# Leyendo las variables de entorno desde el archivo el environment,
# lo cual es aconsejable para no exponer información sensible.
load_dotenv()
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# logueando las variables de entorno para estar seguros de que
# se leyeron correctamente. No haga esto en producción,
# es solo una medida para estar seguros de que tenemos los datos
# necesarios para conectarnos a la base de datos.
_logger.info(f"... POSTGRES_USER: {POSTGRES_USER}")
_logger.info(f"... POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")
_logger.info(f"... POSTGRES_DB: {POSTGRES_DB}")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"

_logger.info(f"... DATABASE_URL: {DATABASE_URL}")

# Creando la conexión a la base de datos
engine = create_engine(DATABASE_URL)

# Definición de la tabla 'usuario'.
metadata = MetaData()
Base = declarative_base()

class Usuario(Base):
    __tablename__ = "usuario"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    apellido = Column(String, index=True)
    email = Column(String, index=True)

Base.metadata.create_all(bind=engine)

# Configuración de la sesión de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Configuración de la aplicación FastAPI
app = FastAPI()

# Endpoint para agregar usuario
@app.post("/agregar-usuario/")
async def agregar_usuario(nombre: str, apellido: str, email: str):
    db = SessionLocal()
    usuario = Usuario(nombre=nombre, apellido=apellido, email=email)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    db.close()
    return {"message": "Usuario agregado correctamente"}

# Endpoint para obtener todos los usuarios
@app.get("/usuarios/")
async def obtener_usuarios():
    db = SessionLocal()
    usuarios = db.query(Usuario).all()
    db.close()
    return usuarios

# Endponit para obtener un usuario por su email
@app.get("/usuario/{email}")
async def obtener_usuario(email: str):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    db.close()
    return usuario

# Endpoint para eliminar un usuario por su email
@app.delete("/usuario/{email}")
async def eliminar_usuario(email: str):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    db.delete(usuario)
    db.commit()
    db.close()
    return {"message": "Usuario eliminado correctamente"}

# Endpoint para actualizar un usuario por su email
@app.put("/usuario/{email}")
async def actualizar_usuario(email: str, nombre: str, apellido: str):
    db = SessionLocal()
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    usuario.nombre = nombre
    usuario.apellido = apellido
    db.commit()
    db.close()
    return {"message": "Usuario actualizado correctamente"}


####### TU CODIGO
'''
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
import pandas as pd
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles #para usar css


app = FastAPI()
app.add_middleware(SessionMiddleware,secret_key="Abelito89*")
templates = Jinja2Templates(directory='./Templates')
# Crea una conexión al servidor de PostgreSQL                     (me quede por aqui, configurando consultas de postgres)
conexion = create_engine('postgresql://postgres:Abelito89*@localhost:5432/citas')

# Crea un cursor con el que ejecutar consultas SQL
#cursor = conexion.cursor()

#verificando si se realiza la consulta sql correctamente

#verificando si el dataframe se carga bien
query = "SELECT * FROM \"Citas\""
df = pd.read_sql_query(query, conexion)#.drop('0', axis=1)
df = df.drop('id', axis=1)
print(df)

# Monta la carpeta 'Templates' en la ruta '/static'
app.mount("/static", StaticFiles(directory="Templates/static"), name="static")

@app.get('/formulario_inicio', response_class=HTMLResponse)
def leer_formulario(peticion:Request):
    #global df, lista_categorias, categoria_seleccionada
    
    query = "SELECT * FROM \"Citas\""
    df = pd.read_sql_query(query, conexion)#.drop('0', axis=1)
    df = df.drop('id', axis=1)
    print(df)
    lista_categorias = df['categoria'].unique()
    categoria_seleccionada = peticion.session.get('categoria_seleccionada','-')
    peticion.session['categoria_seleccionada']=categoria_seleccionada
    
    return templates.TemplateResponse('index.html',{'request':peticion, 'lista_categorias':lista_categorias, 'categoria_seleccionada':categoria_seleccionada})

@app.post('/enviar_categoria')
def enviar_categoria(peticion:Request, categoria_seleccionada:str=Form(...)):
    try:
        query = "SELECT * FROM \"Citas\""
        df = pd.read_sql_query(query, conexion)
        df = df.drop('id', axis=1)
        lista_categorias = df['categoria'].unique()
        if categoria_seleccionada == '-':
            return templates.TemplateResponse('index.html',{'request':peticion, 'cita_devuelta':'Seleccione una categoría válida', 'lista_categorias':lista_categorias})
        elif categoria_seleccionada not in df['categoria'].values:
            return f'La categoria {categoria_seleccionada} no existe'
        
        df_filtrado = df[df['categoria'] == categoria_seleccionada]
        serie_aleatoria = df_filtrado.sample(n=1).iloc[0]
        cita_devuelta = serie_aleatoria['cita']
        return templates.TemplateResponse('index.html',{'request':peticion, 'cita_devuelta':cita_devuelta, 'categoria':categoria_seleccionada, 'lista_categorias':lista_categorias})
    except Exception as e:
        return f'Error procesando el archivo {e}'
    
@app.post('/nuevos_datos')
def nueva_cita(peticion:Request, cita:str=Form(...), categoria:str=Form(...)):
    try:
        #nuevo = coleccion.insert_one({'cita':cita, 'categoria':categoria})
        #peticion.session['categoria_seleccionada'] = '-'
        with conexion.cursor() as cursor:
            cursor.execute("INSERT INTO \"Citas\" (cita, categoria) VALUES (%s, %s)", (cita, categoria))
            conexion.commit()
            peticion.session['categoria_seleccionada'] = '-'        
        return Response(status_code=303, headers={'Location': '/formulario_inicio'})
    except Exception as e:
        return {"error":str(e)}
'''
