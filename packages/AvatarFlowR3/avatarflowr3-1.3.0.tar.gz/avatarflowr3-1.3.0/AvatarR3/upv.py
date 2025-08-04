import requests
import json
import gzip
import os
import subprocess

# URLs CORRECTAS (sin espacios)
BASE_API = "https://api.sync.so"
S3_BUCKET = "https://prod-public-sync-user-assets.s3.us-east-1.amazonaws.com"


# === FUNCIONES CORREGIDAS ===

def leer_respuesta(response):
    """Lee la respuesta, descomprime si es gzip, si no, usa texto plano."""
    content = response.content
    if response.headers.get('Content-Encoding') == 'gzip' or b'{"json"' not in content[:10]:
        try:
            return gzip.decompress(content).decode('utf-8')
        except:
            pass  # Si falla, intenta como texto plano
    return content.decode('utf-8')

def iniciar_subida(nombre_archivo, tamano_bytes):
    """Inicia la subida multipart y extrae uploadId, presignedUrl y key."""
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
    print("📤 Iniciando subida...")

    try:
        response = requests.post(url, headers=COMMON_HEADERS, json=data)
    except Exception as e:
        raise Exception(f"Error de conexión: {e}")

    print(f"📡 Status Code: {response.status_code}")

    content = leer_respuesta(response)
    print("🔍 Respuesta cruda:")
    #print(content)

    if response.status_code != 200:
        raise Exception(f"Error HTTP {response.status_code}: {content}")

    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            # Buscamos la línea que tiene el formato [2, 0, [[[{...uploadId...}]]]]
            if isinstance(j, dict) and 'json' in j:
                json_data = j['json']
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    # Estructura: [2, 0, [[[{...}]]]]
                    payload = json_data[2]  # [[[{...}]]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [[{...}]]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # [{...}]
                            if isinstance(obj, list):
                                obj = obj[0]  # Por si acaso
                            if isinstance(obj, dict) and 'uploadId' in obj and 'presignedUrls' in obj:
                                upload_id = obj['uploadId']
                                presigned_url = obj['presignedUrls'][0]['url']
                                key = obj['key']
                                print("✅ Subida iniciada con éxito.")
                                return upload_id, presigned_url, key
        except Exception as e:
            print(f"⚠️ Error al parsear línea JSON: {e}")
            continue

    raise Exception("❌ No se encontró uploadId en la respuesta. Posible token inválido.")

def agregar_franja_negra(video_entrada, video_salida):
    """
    Agrega una franja negra de 70 píxeles en la parte superior del video.
    """
    if not os.path.exists(video_entrada):
        print(f"⚠️ El archivo no existe.")
        return

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", "pad=iw:ih+70:0:70:black",  # Agregar franja negra arriba
        "-c:a", "copy",
        video_salida
    ]

    try:
        proceso = subprocess.run(comando, check=True, stderr=subprocess.STDOUT)
        #print(f"✅ Franja negra agregada: {video_salida}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al procesar el video:\n{e.output.decode()}")

def recortar_franja_negra(video_entrada, video_salida):
    """
    Recorta una franja negra de 70 píxeles en la parte superior del video.
    """
    if not os.path.exists(video_entrada):
        print(f"⚠️ El archivo no existe.")
        return

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", "crop=iw:ih-70:0:70",  # Recortar 70 píxeles desde arriba
        "-c:a", "copy",
        video_salida
    ]

    try:
        proceso = subprocess.run(comando, check=True, stderr=subprocess.STDOUT)
        #print(f"✅ Franja negra recortada: {video_salida}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al procesar el video:\n{e.output.decode()}")

def subir_fragmento(presigned_url, archivo_path):
    print("📤 Subiendo fragmento al bucket S3...")

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

    with open(archivo_path, 'rb') as f:
        contenido = f.read()

    headers = S3_HEADERS.copy()
    headers['Content-Length'] = str(len(contenido))

    response = requests.put(presigned_url, data=contenido, headers=headers)

    if response.status_code == 200:
        etag = response.headers.get('ETag', '').strip('"')
        print("✅ Fragmento subido.")
        return etag
    else:
        raise Exception(f"Error en PUT: {response.status_code}, {response.text}")

def completar_subida(upload_id, etag, nombre_archivo):
    """Confirma la subida multipart (POST /fileStorage.completeMultipartUpload)."""
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
    print("✅ Completando subida...")
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
                if isinstance(json_data, list) and json_data[0] == 2:
                    # Busca "publicUrl" en el objeto
                    if len(json_data) > 2 and isinstance(json_data[2], list):
                        obj = json_data[2][0][0]
                        if isinstance(obj, dict) and 'publicUrl' in obj:
                            return obj['publicUrl']
        except Exception as e:
            print(f"⚠️ Error parsing line: {e}")
            continue
    raise Exception("No se encontró URL pública.")

def debug_response(func):
    def wrapper(*args, **kwargs):
        print(f"🔍 Ejecutando {func.__name__}")
        result = func(*args, **kwargs)
        print(f"✅ {func.__name__} completado.")
        return result
    return wrapper

def crear_recurso(public_url, project_id="a449159c-7efa-4db6-8100-a408db68a538"):
    """Crea el asset en el proyecto (POST /assets.create)."""
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

    url = f"{BASE_API}/trpc/assets.create?batch=1"
    data = {
        "0": {
            "json": {
                "visibility": "USER",
                "projectId": project_id,
                "url": public_url,
                "type": "VIDEO",
                "name": os.path.basename(public_url).split('?')[0]
            }
        }
    }
    print("🎨 Creando recurso...")
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
                    payload = json_data[2]  # [[{...}]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [{...}]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # {...}
                            if isinstance(obj, dict) and 'id' in obj:
                                asset_id = obj['id']
                                print("✅ Recurso creado.")
                                return asset_id
        except Exception as e:
            print(f"⚠️ Error al parsear línea: {e}")
            continue

    raise Exception("No se creó el recurso. Posible error en projectId o URL.")

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

    print("🔍 Obteniendo recurso...")
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
                # Buscamos: [2, 0, [[{...}]]]
                if isinstance(json_data, list) and len(json_data) >= 3 and json_data[0] == 2:
                    payload = json_data[2]  # [[{...}]]
                    if isinstance(payload, list) and len(payload) > 0:
                        inner = payload[0]  # [{...}]
                        if isinstance(inner, list) and len(inner) > 0:
                            obj = inner[0]  # {...}
                            if isinstance(obj, dict) and 'id' in obj and obj['id'] == asset_id:
                                print("✅ Recurso obtenido.")
                                return obj
        except Exception as e:
            print(f"⚠️ Error al parsear línea: {e}")
            continue

    raise Exception("No se encontró el recurso solicitado.")

# === FUNCIÓN PRINCIPAL ===
def subir_video_a_sync_so(ruta_video, project_id="a449159c-7efa-4db6-8100-a408db68a538"):
    if not os.path.exists(ruta_video):
        raise FileNotFoundError(f"Archivo no encontrado: {ruta_video}")

    nombre_archivo = os.path.basename(ruta_video)
    tamano = os.path.getsize(ruta_video)

    try:
        upload_id, presigned_url, key = iniciar_subida(nombre_archivo, tamano)
        etag = subir_fragmento(presigned_url, ruta_video)
        public_url = completar_subida(upload_id, etag, nombre_archivo)
        asset_id = crear_recurso(public_url, project_id)
        info = obtener_recurso(asset_id)

        return info['id'], info['name'], info['url']

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def up_video(VIDEO_PATH):
    agregar_franja_negra("/tmp/video.mp4", "/tmp/video_f.mp4")
    # === EJECUCIÓN ===
    VIDEO_PATH = "/tmp/video_f.mp4"
    project_id = os.environ.get("PROJECT_ID")

    asset_id_video, info_name_video, info_url_video = subir_video_a_sync_so(VIDEO_PATH, project_id)
    if asset_id_video:
      print("✅ Video subido exitosamente!")
      os.environ["ASSET_ID_VIDEO"] = asset_id_video
      os.environ["INFO_NAME_VIDEO"] = info_name_video
      os.environ["INFO_URL_VIDEO"] = info_url_video
      #print("ASSET_ID", asset_id_video)
      #print("INFO_NAME", info_name_video)
      #print("INFO_URL", info_url_video)
