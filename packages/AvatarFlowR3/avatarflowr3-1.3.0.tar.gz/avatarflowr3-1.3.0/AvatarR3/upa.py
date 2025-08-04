import time
import requests
import json
import gzip
import os


BASE_API = "https://api.sync.so"
S3_BUCKET = "https://prod-public-sync-user-assets.s3.us-east-1.amazonaws.com"


# === FUNCIÓN DE LECTURA DE RESPUESTA (igual que en el video) ===
def leer_respuesta(response):
    content = response.content
    if response.headers.get('Content-Encoding') == 'gzip':
        try:
            return gzip.decompress(content).decode('utf-8')
        except:
            pass
    try:
        return content.decode('utf-8')
    except:
        return content.decode('latin1')

# === FUNCIONES CORREGIDAS (copiadas del video que funciona) ===

def iniciar_subida(nombre_archivo, tamano_bytes):
    """Inicia la subida multipart."""
    session_token = os.environ.get("ACCESS_TOKEN")
    POSTHOG_COOKIE = "%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829914273%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"

    COMMON_HEADERS = {
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
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog={POSTHOG_COOKIE}"
    }
    url = f"{BASE_API}/trpc/fileStorage.initiateMultipartUpload?batch=1"
    data = {
        "0": {
            "json": {
                "isPublic": True,
                "parts": 1,
                "fileName": nombre_archivo,
                "contentLength": tamano_bytes
            }
        }
    }
    print("📤 Iniciando subida de audio...")
    try:
        response = requests.post(url, headers=COMMON_HEADERS, json=data)
    except Exception as e:
        raise Exception(f"Error de conexión: {e}")

    print(f"📡 Status Code: {response.status_code}")
    content = leer_respuesta(response)
    print("🔍 Respuesta cruda:")
    #print(content)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            if isinstance(j, dict) and 'json' in j:
                json_data = j['json']
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    payload = json_data[2]  # [[[{...}]]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [[{...}]]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # [{...}]
                            if isinstance(obj, dict) and 'uploadId' in obj:
                                upload_id = obj['uploadId']
                                presigned_url = obj['presignedUrls'][0]['url']
                                key = obj['key']
                                print("✅ Subida de audio iniciada.")
                                return upload_id, presigned_url, key
        except Exception as e:
            print(f"⚠️ Error al parsear línea: {e}")
            continue
    raise Exception("❌ No se encontró uploadId.")

def subir_fragmento(presigned_url, archivo_path):
    """Sube el archivo al presigned URL."""
    S3_HEADERS = {
        "Host": "prod-public-sync-user-assets.s3.us-east-1.amazonaws.com",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    print("📤 Subiendo audio al bucket S3...")
    with open(archivo_path, 'rb') as f:
        contenido = f.read()
    headers = S3_HEADERS.copy()
    headers['Content-Length'] = str(len(contenido))
    response = requests.put(presigned_url, data=contenido, headers=headers)
    if response.status_code == 200:
        etag = response.headers.get('ETag', '').strip('"')
        print("✅ Audio subido.")
        return etag
    else:
        raise Exception(f"Error en PUT: {response.status_code}, {response.text}")

def completar_subida(upload_id, etag, nombre_archivo):
    """Completa la subida multipart (POST /fileStorage.completeMultipartUpload)."""
    session_token = os.environ.get("ACCESS_TOKEN")
    POSTHOG_COOKIE = "%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829914273%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"

    COMMON_HEADERS = {
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
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog={POSTHOG_COOKIE}"
    }

    url = f"{BASE_API}/trpc/fileStorage.completeMultipartUpload?batch=1"
    data = {
        "0": {
            "json": {
                "uploadId": upload_id,
                "parts": [{"ETag": etag, "PartNumber": 1}],
                "fileName": nombre_archivo,
                "isPublic": True
            }
        }
    }
    print("✅ Completando subida de audio...")
    response = requests.post(url, headers=COMMON_HEADERS, json=data)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    content = leer_respuesta(response)
    print("🔍 Respuesta de completar_subida:")
    #print(content)

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            if isinstance(j, dict) and 'json' in j:
                json_data = j['json']
                # Buscamos: [2, 0, [[{...}]]] y que tenga "publicUrl"
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    payload = json_data[2]  # [[[{...}]]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [[{...}]]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # [{...}]
                            if isinstance(obj, dict) and 'publicUrl' in obj:
                                public_url = obj['publicUrl'].strip()
                                print("✅ Subida completada.")
                                return public_url
        except Exception as e:
            print(f"⚠️ Error parsing line: {e}")
            continue

    raise Exception("No se encontró URL pública.")

def crear_recurso(public_url, project_id="a449159c-7efa-4db6-8100-a408db68a538", nombre_audio=None):
    """Crea el recurso de tipo AUDIO."""
    session_token = os.environ.get("ACCESS_TOKEN")
    POSTHOG_COOKIE = "%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829914273%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"

    COMMON_HEADERS = {
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
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog={POSTHOG_COOKIE}"
    }

    if nombre_audio is None:
        nombre_audio = os.path.basename(public_url).split('?')[0]

    url = f"{BASE_API}/trpc/assets.create?batch=1"
    data = {
        "0": {
            "json": {
                "visibility": "USER",
                "projectId": project_id,
                "url": public_url.strip(),  # limpiar espacios
                "type": "AUDIO",
                "name": nombre_audio
            }
        }
    }
    print("🎵 Creando recurso de audio...")
    response = requests.post(url, headers=COMMON_HEADERS, json=data)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    content = leer_respuesta(response)
    print("🔍 Respuesta de crear_recurso:")
    #print(content)

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            if isinstance(j, dict) and 'json' in j:
                json_data = j['json']
                # Buscamos: [2, 0, [[{...}]]]
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    payload = json_data[2]  # [[[{...}]]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [[{...}]]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # [{...}]
                            if isinstance(obj, dict) and 'id' in obj:
                                asset_id = obj['id']
                                print("✅ Recurso de audio creado.")
                                return asset_id
        except Exception as e:
            print(f"⚠️ Error al parsear línea: {e}")
            continue

    raise Exception("No se creó el recurso de audio.")

def obtener_recurso(asset_id):
    """Obtiene el recurso creado (GET /assets.get)."""
    session_token = os.environ.get("ACCESS_TOKEN")
    POSTHOG_COOKIE = "%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829914273%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"

    COMMON_HEADERS = {
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
        "Accept-Encoding": "gzip, deflate",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog={POSTHOG_COOKIE}"
    }

    input_data = json.dumps({"0": {"json": {"id": asset_id}}})
    query = f"?batch=1&input={requests.utils.quote(input_data)}"
    url = f"{BASE_API}/trpc/assets.get{query}"

    print("🔍 Obteniendo recurso de audio...")
    response = requests.get(url, headers=COMMON_HEADERS)

    if response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")

    content = leer_respuesta(response)
    print("🔍 Respuesta de obtener_recurso:")
    #print(content)

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            if isinstance(j, dict) and 'json' in j:
                json_data = j['json']
                # Buscamos: [2, 0, [[{...}]]] con el id correcto
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    payload = json_data[2]  # [[[{...}]]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [[{...}]]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # [{...}]
                            if isinstance(obj, dict) and 'id' in obj and obj['id'] == asset_id:
                                print("✅ Recurso obtenido.")
                                return obj
        except Exception as e:
            print(f"⚠️ Error al parsear línea: {e}")
            continue

    raise Exception("No se encontró el recurso solicitado.")

# === FUNCIÓN PRINCIPAL PARA AUDIO ===
def subir_audio_a_sync_so(ruta_audio, project_id="a449159c-7efa-4db6-8100-a408db68a538", nombre_audio=None):
    """
    Sube un archivo de audio a sync.so y crea un recurso de tipo AUDIO.
    """
    if not os.path.exists(ruta_audio):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_audio}")

    nombre_archivo = os.path.basename(ruta_audio)
    tamano = os.path.getsize(ruta_audio)

    try:
        upload_id, presigned_url, key = iniciar_subida(nombre_archivo, tamano)
        etag = subir_fragmento(presigned_url, ruta_audio)
        public_url = completar_subida(upload_id, etag, nombre_archivo)
        asset_id = crear_recurso(public_url, project_id, nombre_audio or nombre_archivo)
        info = obtener_recurso(asset_id)

        return info['id'], info['name'], info['url']

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

# Generar nombre dinámico
def generar_nombre():
    timestamp = int(time.time())
    return f"AUDIO-input-{timestamp}.mp3"

def up_audio(AUDIO_PATH):
    nombre_audio = generar_nombre()
    project_id = os.environ.get("PROJECT_ID")

    asset_id_audio, info_name_audio, info_url_audio = subir_audio_a_sync_so(AUDIO_PATH, project_id, nombre_audio)
    if asset_id_audio:
      print("✅ Audio subido exitosamente!")
      os.environ["ASSET_ID_AUDIO"] = asset_id_audio
      os.environ["INFO_NAME_AUDIO"] = info_name_audio
      os.environ["INFO_URL_AUDIO"] = info_url_audio
      #print("ASSET_ID_AUDIO", asset_id_audio)
      #print("INFO_NAME_AUDIO", info_name_audio)
      #print("INFO_URL_AUDIO", info_url_audio)