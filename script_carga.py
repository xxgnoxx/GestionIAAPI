from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import httpx
import os
from datetime import date

script = FastAPI()

# Crea la estructura en la que se reciben los datos; en este caso, ajustada a la tabla cuenta
class DatosCuenta(BaseModel):
    idcuenta: int
    moneda: str
    saldo: float
    estado: bool

class DatosTransaccion(BaseModel):
    idtransaccion: int
    idcuentaorigen: int
    idcuentadestino: int
    monto: float
    fecha: date
    estadotransaccion: bool

class DatosLibro(BaseModel):
    idlibro: int
    idtransaccion: int
    saldo: float
    monto: float
    fechalibro: date

# La URL a la API de destino; esta es la API de Supabase
endpoint_supabase_cuenta = 'https://amhwbjhaueiicxozdllx.supabase.co/rest/v1/cuenta'
endpoint_supabase_transaccion = 'https://amhwbjhaueiicxozdllx.supabase.co/rest/v1/transaccion'
endpoint_supabase_libro = 'https://amhwbjhaueiicxozdllx.supabase.co/rest/v1/libro'


# Script para recibir datos con POST y enviarlos a la API de supabase; para datos a la tabla cuenta de data_copper
# El endpoint es '/enviar-datos', el cual solo acepta POST
@script.post("/enviar-datos")
async def enviar_datos(request: Request):
    # Revisa el JSON para ver el tipo de contenido, si es válido, y en caso de que sea válido, verificar el tipo de tabla
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Los datos no son válidos")

    if not payload:
        raise HTTPException(status_code=400, detail="El JSON está vacío")

    # Detección: detecta qué tipo de datos es según la estructura de datos para enviarlo a la tabla apropiada
    # Incluye prints para que la consola o el Docker muestre el tipo de tabla detectada, si detecta alguna
    
    # Tabla "cuenta"
    if "idcuenta" and "moneda" and "saldo" and "estado" in payload:
        endpoint_supabase = endpoint_supabase_cuenta
        print("Datos detectados como 'cuenta'")
    # Tabla "transaccion"
    elif "idtransaccion" and "idcuentaorigen" and "idcuentadestino" and "monto" and "fecha" and "estadotransaccion" in payload:
        endpoint_supabase = endpoint_supabase_transaccion
        print("Datos detectados como 'transaccion'")
    # Tabla "libro"
    elif "idlibro" and "idtransaccion" and "saldo" and "monto" and "fechalibro" in payload:
        endpoint_supabase = endpoint_supabase_libro
        print("Datos detectados como 'libro'")
    # Si no tiene ninguno de los conjuntos de datos posibles, se rechaza
    else:
        print("ERROR: Los datos no corresponden a ninguna tabla")
        raise HTTPException(
            status_code=422, 
            detail="Estos datos no pertenecen a una tabla válida, ya que no contiene ningún tipo de ID válida."
        )
    
    
    # Detección de headers: detecta si el Schema está presente, y el valor que corresponde
    # Esto permite enviar a un esquema específico con el header correspondiente

    # Si el header Schema dice copper
    if request.headers.get("Schema") == "copper":
        esquema_seleccionado = "data_copper"
        print("Estos datos se enviarán al esquema data_copper")
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

    # Envío de información a la API de Supabase
    async with httpx.AsyncClient() as client:

        # Headers: 
        # apikey para permitir acceso
        # Content-Type para indicar que es un json
        # Content-Profile para indicar el esquema al que se va a enviar
        headers_supabase = {
            "apikey": os.getenv("PASSWORD_SUPABASE"),  # Variable de entorno; contraseña en .env
            "Content-Type": "application/json",
            "Content-Profile": esquema_seleccionado
        }

        # Envía los datos, usando headers_supabase para asegurar que se conecte correctamente
        try:
            # Envía la respuesta, con los datos correspondientes y los headers para acceder, con un tiempo de respuesta máximo de 10 segundos
            respuesta = await client.post(endpoint_supabase, json=payload, headers=headers_supabase,timeout=10.0)
            # Revisa si el POST funcionó correctamente
            respuesta.raise_for_status()
        # Si hay un error HTTP, envía un mensaje a la consola y a la API con información y el código de respuesta
        except httpx.HTTPStatusError as eh:
            print(f"ERROR {eh.response.status_code}: {str(eh)}")
            return {
                "status": "ERROR: No se logró una conexión a la API.",
                "detalles_api": f"Código: {eh.response.status_code}",
                "error": str(eh)
            }
        # Si hay un error de otro tipo, envía un mensaje a la consola y la API con la información del error
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return {
                "status": "Hubo un error desconocido.",
                "error": str(e)
            }
    print("Los datos fueron enviados con éxito")
    return {"status": "Los datos fueron enviados correctamente."}