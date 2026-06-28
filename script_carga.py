from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
from datetime import date
from datetime import datetime

script = FastAPI()

# Crea la estructura en la que se reciben los datos; en este caso, ajustada a la tabla cuenta
class DatosCuenta(BaseModel):
    moneda: str
    saldo: float
    estado: bool

class DatosTransaccion(BaseModel):
    idcuentaorigen: int
    idcuentadestino: int
    monto: float
    fecha: date
    estadotransaccion: bool

class DatosLibro(BaseModel):
    idtransaccion: int
    saldo: float
    monto: float
    fechalibro: date

# La URL a la API de destino; esta es la API de Supabase
endpoint_supabase_cuenta = os.getenv("SUPABASE_API_CUENTA")
endpoint_supabase_transaccion = os.getenv("SUPABASE_API_TRANSACCION")
endpoint_supabase_libro = os.getenv("SUPABASE_API_LIBRO")


# Script para recibir datos con POST y enviarlos a la API de supabase; para datos a la tabla cuenta de data_bronze
# El endpoint es '/enviar-datos', el cual solo acepta POST
@script.post("/enviar-datos")
async def enviar_datos(request: Request):
    # Timestamp para marcar el tiempo de inicio
    timestampstart = datetime.now().timestamp()
    print(f'Tiempo de inicio API: {datetime.fromtimestamp(timestampstart)}')
    
    # Revisa el JSON para ver el tipo de contenido, si es válido, y en caso de que sea válido, verificar el tipo de tabla
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Los datos no son válidos")

    if not payload:
        raise HTTPException(status_code=400, detail="El JSON está vacío")
    
    

    # Detección: detecta qué tipo de datos es según la estructura de datos para enviarlo a la tabla apropiada
    # Incluye prints para que la consola o el Docker muestre el tipo de tabla detectada, si detecta alguna
    
    # Detección de headers: detecta si el Schema está presente, y el valor que corresponde
    # Esto permite enviar a un esquema específico con el header correspondiente

    timestampheaders = datetime.now().timestamp()
    print(f'Lectura de headers iniciada: {datetime.fromtimestamp(timestampheaders)}')  
    # Si el header Table dice cuenta
    if request.headers.get("Table") == "cuenta":
        endpoint_supabase = endpoint_supabase_cuenta
        print("Estos datos se enviarán a la tabla cuenta")
    # Si el header Table dice transaccion
    elif request.headers.get("Table") == "transaccion":
        endpoint_supabase = endpoint_supabase_transaccion
        print("Estos datos se enviarán a la tabla transaccion")
    # Si el header Table dice libro
    elif request.headers.get("Table") == "libro":
        endpoint_supabase = endpoint_supabase_libro
        print("Estos datos se enviarán a la tabla libro")
    # Si no hay una tabla
    else:
        print("ERROR: El request no tiene un header 'Tabla' con la tabla correspondiente.")
        endpoint_supabase = 'none'
    
    # Detección de headers: detecta si el Schema está presente, y el valor que corresponde
    # Esto permite enviar a un esquema específico con el header correspondiente

    # Si el header Schema dice bronze
    if request.headers.get("Schema") == "bronze":
        esquema_seleccionado = "data_bronze"
        print("Estos datos se enviarán al esquema data_bronze")
    # Si el header Schema dice silver
    elif request.headers.get("Schema") == "silver":
        esquema_seleccionado = "data_silver"
        print("Estos datos se enviarán al esquema data_silver")
    # Si el header Schema dice gold
    elif request.headers.get("Schema") == "gold":
        esquema_seleccionado = "data_gold"
        print("Estos datos se enviarán al esquema data_gold")
    # Si el header Schema dice cold
    elif request.headers.get("Schema") == "cold":
        esquema_seleccionado = "data_cold"
        print("Estos datos se enviarán al esquema data_cold")
    # Si no hay un esquema
    else:
        print("ERROR: El request no tiene un header 'Schema' con el esquema correspondiente.")
        esquema_seleccionado = 'none'
    timestampheadersend = datetime.now().timestamp()
    print(f'Lectura de headers terminada: {datetime.fromtimestamp(timestampheadersend)}')

    # Envío de información a la API de Supabase
    timestamppost = datetime.now().timestamp()
    print(f'Envío de datos iniciado: {datetime.fromtimestamp(timestamppost)}')
    async with httpx.AsyncClient() as client:

        # Headers: 
        # apikey para permitir acceso
        # Content-Type para indicar que es un json
        # Content-Profile para indicar el esquema al que se va a enviar
        headers_supabase = {
            "apikey": os.getenv("PASSWORD_SUPABASE"),  # Variable de entorno; contraseña en .env
            "Content-Type": "application/json",
            "Content-Profile": esquema_seleccionado,
            "Prefer": "return=minimal"
        }

        # Envía los datos, usando headers_supabase para asegurar que se conecte correctamente
        try:
            # Envía la respuesta, con los datos correspondientes y los headers para acceder, con un tiempo de respuesta máximo de 10 segundos
            respuesta = await client.post(endpoint_supabase, json=payload, headers=headers_supabase,timeout=10.0)
            # Revisa si el POST funcionó correctamente
            respuesta.raise_for_status()
        # Si hay un error HTTP, envía un mensaje a la consola y a la API con información y el código de respuesta
        except httpx.HTTPStatusError as eh:
            try:
                detalles_supabase = eh.response.json()
            except Exception:
                detalles_supabase = eh.response.text

            print(f"ERROR {eh.response.status_code} DESDE SUPABASE: {detalles_supabase}")
            return {
                "status": "ERROR: Supabase rechazó la solicitud.",
                "codigo_http": eh.response.status_code,
                "detalle_supabase": detalles_supabase
            }
        # Si hay un error de otro tipo, envía un mensaje a la consola y la API con la información del error
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return {
                "status": "Hubo un error desconocido.",
                "error": str(e)
            }
    print("Los datos fueron enviados con éxito")
    timestampend = datetime.now().timestamp()
    print(f'Tiempo de fin API: {datetime.fromtimestamp(timestampend)}')
    return {"status": "Los datos fueron enviados correctamente."}