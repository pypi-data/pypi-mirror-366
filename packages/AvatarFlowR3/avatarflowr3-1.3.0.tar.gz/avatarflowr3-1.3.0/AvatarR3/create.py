import requests
import json
import re
import random
import unicodedata
import os

# Listas de nombres y apellidos (con posibles acentos y ñ)
nombres = [
    "Ana", "Luis", "María", "Carlos", "Sofía", "Javier", "Lucía", "Andrés",
    "Valentina", "Miguel", "Camila", "Diego", "Isabella", "Alejandro", "Paula",
    "Fernando", "Daniela", "Roberto", "Carla", "José", "Elena", "Raúl",
    "Cristina", "Hugo", "Natalia", "Pablo", "Verónica", "Juan", "Andrea", "Pedro"
]

apellidos = [
    "García", "Rodríguez", "Martínez", "Hernández", "López", "González",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Jiménez",
    "Cruz", "Gómez", "Díaz", "Vásquez", "Ortiz", "Castillo", "Romero",
    "Ruiz", "Mendoza", "Chávez", "Núñez", "Juárez", "Ibarra", "Salazar",
    "Bravo", "Rivas", "Cabrera", "Muñoz", "Niño"
]

# Función para eliminar acentos y caracteres no ASCII (como ñ, ç, etc.)
def eliminar_caracteres_especiales(texto):
    # Reemplazar manualmente la ñ y Ñ
    texto = texto.replace('ñ', 'ni').replace('Ñ', 'Ni')
    # Normalizar el texto y eliminar acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')  # Elimina marcas diacríticas
    return texto.encode('ascii', 'ignore').decode('ascii')  # Solo ASCII

# Función para generar nombre aleatorio limpio
def generar_nombre_aleatorio():
    nombre = random.choice(nombres)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)
    # Combinar y limpiar
    nombre_completo = f"{nombre}{apellido1}{apellido2}"
    nombre_limpio = eliminar_caracteres_especiales(nombre_completo)
    return nombre_limpio.lower()  # Todo en minúsculas y sin espacios



def crear_proyecto(project_name, session_token):
    # Entradas editables por el usuario

    # Validar que no estén vacíos
    if not session_token:
        print("❌ El session token es obligatorio.")
        return
    if not project_name:
        print("❌ El nombre del proyecto es obligatorio.")
        return

    # URL y cabeceras
    url = "https://api.sync.so/trpc/projects.create?batch=1"
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829732513%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D",
        "Accept-Encoding": "gzip, deflate",
    }

    # Cuerpo de la solicitud (batched trpc)
    payload = {
        "0": {
            "json": {
                "name": project_name,
                "description": "",
                "visibility": "USER",
                "mode": "CREATOR"
            }
        }
    }

    try:
        # Enviar solicitud POST
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            # La respuesta es en formato JSONL (JSON Lines)
            lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            project_data = None

            # Buscar la línea que contiene el objeto "data" con el proyecto
            for line in lines:
                try:
                    parsed = json.loads(line)
                    # Buscar si contiene "data" con "id" y "name"
                    if "json" in parsed and isinstance(parsed["json"], list) and len(parsed["json"]) > 2:
                        data_part = parsed["json"][2]
                        if isinstance(data_part, list) and len(data_part) > 0:
                            inner = data_part[0]
                            if isinstance(inner, list) and len(inner) > 0:
                                project_candidate = inner[0]
                                if isinstance(project_candidate, dict) and "id" in project_candidate:
                                    project_data = project_candidate
                                    break
                except json.JSONDecodeError:
                    continue

            if project_data:
                print("✅ Proyecto creado exitosamente!")
                #print(f"📌 ID: {project_data['id']}")
                #print(f"👥 Organization ID: {project_data['organizationId']}")
                #print(f"👤 User ID: {project_data['userId']}")
                #print(f"📛 Nombre: {project_data['name']}")
                return project_data["id"], project_data["organizationId"], project_data["userId"], project_data["name"]

            else:
                print("❌ No se pudo extraer la información del proyecto.")
                print("📄 Respuesta completa (depuración):")
                #print(response.text)
        else:
            print(f"❌ Error {response.status_code}: No se pudo crear el proyecto.")
            #print(response.text)

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")


def create_projects():
    # Ejecutar la función
    session_token = os.environ.get("ACCESS_TOKEN")
    # Generar un nombre
    nombre_aleatorio = generar_nombre_aleatorio()
    print("Nombre generado:", nombre_aleatorio)

    project_name = nombre_aleatorio
    project_id, organizationId, userId, name = crear_proyecto(project_name, session_token)
    if project_id:
      print("✅ Proyecto creado exitosamente!")
      #print(project_id)
      #print(organizationId)
      #print(userId)
      #print(name)
      os.environ["PROJECT_ID"] = project_id
      os.environ["ORGANIZATION_ID"] = organizationId
      os.environ["USER_ID"] = userId
      os.environ["PROJECT_NAME"] = name
