# Usa python 3.12
FROM python:3.12-slim

# El punto indica que el directorio de trabajo es el mismo donde se está creando la imagen
WORKDIR .

# Copia el archivo requirements.txt
COPY /requirements.txt .

# Descarga los requerimientos en el archivo; si el requirements.txt está vacío, avanza de igual manera
RUN pip install --no-cache-dir -r requirements.txt

# Copia el directorio en el contenedor
COPY script_carga.py .

# Puerto en el que funcionará FastAPI
EXPOSE 8000

# Comando para ejecutar el script usando Uvicorn
CMD ["uvicorn", "script_carga:script", "--host", "0.0.0.0", "--port", "8000"]