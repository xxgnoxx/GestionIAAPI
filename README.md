# GestionIAAPI 
Repositorio que contiene la API de carga de datos, conectándose a la API de Supabase. La API está subida a Render utilizando este repositorio.

# Estructura  
├──requirements.txt = Requerimientos del contenedor  
├──Dockerfile = Archivo Docker para ejecutar el contenedor  
├──README.md = Archivo readme  
├──script_carga.py = Script principal de API  
├──.gitignore = Archivos para no subir en el repositorio  

# Instrucciones de instalación (ejecución local)  
1. Clonar el repositorio (git clone https://github.com/xxgnoxx/GestionIAAPI)   
2. Asegurar que Docker Desktop esté instalado y ejecutado  
4. Instalar el contenedor usando 'docker build -t api-carga .'
5. Ejecutar el contenedor usando 'docker run --rm api-carga'  

# Desinstalación  
1. Ejecutar 'docker-compose down' en la carpeta raíz  
2. Eliminar la carpeta del proyecto  
