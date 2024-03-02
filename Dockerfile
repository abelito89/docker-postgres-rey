# Usa la imagen base de Python 3.11
FROM python:3.11

# Establece el directorio de trabajo en /app
WORKDIR /Proyecto_docker1

# Copia el archivo de requisitos al contenedor
COPY requirements.txt /Proyecto_docker1

# Instala las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r /Proyecto_docker1/requirements.txt

# Copia el código fuente de tu aplicación al contenedor
COPY . .

# Expone el puerto 8000 para FastAPI
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación cuando el contenedor se inicie
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
