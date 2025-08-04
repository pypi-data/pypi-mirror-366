#@title GenAvatar
import os
import requests
import json
import time
import subprocess
from upa import *
from upv import *
from create import *
from reg import *

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

def delete_project(project_id, session_token):
    """
    Elimina un proyecto en Sync.so usando el endpoint trpc/projects.delete.
    
    Args:
        project_id (str): ID del proyecto (ej: ea67d649-0648-...)
        session_token (str): Tu cookie __Secure-sync.session_token
        user_id (str): Tu ID de usuario (UUID)
    
    Returns:
        dict: Respuesta de éxito o error.
    """
    
    url = "https://api.sync.so/trpc/projects.delete?batch=1"
    
    # Cuerpo de la solicitud
    payload = {
        "0": {
            "json": {
                "id": project_id
            }
        }
    }
    
    # Headers
    headers = {
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
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%22f1aeffaa-2f4f-4d9a-b5d7-3a52d8b9766d%22%2C%22%24sesid%22%3A%5B{int(time.time() * 1000)}%2C%2201986d40-63fb-7b94-a86e-478dd6680a74%22%2C{int(time.time() * 1000) - 100000}%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"
    }
    

    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            # Procesar JSONL
            lines = [line.strip() for line in response.text.split('\n') if line.strip()]
            for line in lines:
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict) and 'json' in parsed:
                        data = parsed['json']
                        # Buscar si devuelve el ID del proyecto eliminado
                        if isinstance(data, list) and len(data) > 0:
                            if isinstance(data[0], list) and len(data[0]) > 0:
                                result = data[0][0]
                                if isinstance(result, dict) and result.get("id") == project_id:
                                    return {
                                        "success": True,
                                        "message": "🗑️ Proyecto eliminado correctamente",
                                        "project_id": project_id
                                    }
                except:
                    continue
            return {"success": True, "message": "Eliminación enviada (respuesta sin estructura clara)"}
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "details": response.text
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }



def delete_generation(generation_id, session_token):
    """
    Elimina una generación en Sync.so usando el endpoint trpc/generations.delete.
    
    Args:
        generation_id (str): ID de la generación (ej: 2031d9a1-4023-...)
        session_token (str): Tu cookie __Secure-sync.session_token
        user_id (str): Tu ID de usuario (UUID)
    
    Returns:
        dict: Respuesta de la API o mensaje de error.
    """
    
    url = "https://api.sync.so/trpc/generations.delete?batch=1"
    
    # Cuerpo de la solicitud
    payload = {
        "0": {
            "json": {
                "id": generation_id
            }
        }
    }
    
    # Headers
    headers = {
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
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753830464848%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"
    }
    

    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            # Procesar JSONL
            lines = [line.strip() for line in response.text.split('\n') if line.strip()]
            for line in lines:
                try:
                    parsed = json.loads(line)
                    if isinstance(parsed, dict) and 'json' in parsed:
                        data = parsed['json']
                        # Buscar si tiene deletedAt
                        if isinstance(data, list) and len(data) > 0:
                            gen = data[0]
                            if isinstance(gen, dict) and gen.get("deletedAt"):
                                return {
                                    "success": True,
                                    "message": "✅ Generación eliminada correctamente",
                                    "deleted_at": gen["deletedAt"]
                                }
                except:
                    continue
            return True
        else:
            return False
    
    except Exception as e:
        return False




def wait_for_completion_and_get_url(project_id, session_token, max_wait=600, check_interval=10):
    """
    Espera hasta que el proyecto tenga status COMPLETED y extrae outputMediaUrl.
    Funciona con la estructura real de trpc + JSONL.
    """
    url = f"https://api.sync.so/trpc/projects.get?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22id%22%3A%22{project_id}%22%7D%7D%7D"

    headers = {
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
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog=%7B%22distinct_id%22%3A%22f1aeffaa-2f4f-4d9a-b5d7-3a52d8b9766d%22%2C%22%24sesid%22%3A%5B{int(time.time() * 1000)}%2C%2201986d40-63fb-7b94-a86e-478dd6680a74%22%2C{int(time.time() * 1000) - 100000}%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"
    }

    start_time = time.time()
    print(f"⏳ Esperando que el proyecto...")

    while True:
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(f"❌ Error HTTP {response.status_code}")
                time.sleep(check_interval)
                continue

            # Procesar JSONL línea por línea
            project_data = None

            for line in response.text.strip().split('\n'):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict) and 'json' in obj:
                        data = obj['json']
                        # Caso 1: [index,0,[[{proyecto}]]]
                        if isinstance(data, list) and len(data) >= 3 and isinstance(data[2], list):
                            inner_list = data[2][0]  # [[{...}]]
                            if isinstance(inner_list, list) and len(inner_list) > 0:
                                item = inner_list[0]
                                if isinstance(item, dict) and "generations" in item:
                                    project_data = item
                                    break
                        # Caso 2: {"0": {proyecto}}
                        elif isinstance(data, dict) and "0" in data:
                            if isinstance(data["0"], dict) and "generations" in data["0"]:
                                project_data = data["0"]
                                break
                except Exception as e:
                    continue  # Ignorar errores de parsing

            if not project_data:
                print("⚠️ Aún no se reciben datos del proyecto...")
                time.sleep(check_interval)
                continue

            # Extraer generación
            generation = project_data.get("generations", [{}])[0]
            status = generation.get("status")
            output_url = generation.get("outputMediaUrl")

            print(f"🔄 Estado: {status} | {time.strftime('%H:%M:%S')}")

            if status == "COMPLETED" and output_url:
                print("🎉 ¡Generación completada!")
                #print(f"🔗 outputMediaUrl: {output_url.strip()}")
                return output_url.strip()

            if status in ["FAILED", "ERROR"]:
                print("❌ La generación falló.")
                return None

            time.sleep(check_interval)

            if time.time() - start_time > max_wait:
                print(f"⏰ Tiempo máximo de espera ({max_wait}s) alcanzado.")
                return None

        except Exception as e:
            print(f"⚠️ Error: {str(e)}")
            time.sleep(check_interval)

    return None


def download_video(url, filename="/tmp/output.mp4"):
    """Descarga el video desde la URL."""
    print(f"🎥 Descargando video: {filename}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"✅ Video descargado: {filename}")
        # Definir la ruta de la carpeta
        ruta = "/content/video/"
        # Verificar si la carpeta existe
        if not os.path.exists(ruta):
            # Si no existe, crearla
            os.makedirs(ruta)
            print(f"La carpeta ha sido creada.")
        else:
            print(f"La carpeta ya existe.")
            # Recortar la franja negra
        recortar_franja_negra("/tmp/output.mp4", "/content/video/output.mp4")
        return True
    except Exception as e:
        print(f"❌ Error al descargar: {str(e)}")
        return False




def generar_lipsync(video_asset_id, audio_asset_id, project_id, session_token, version):

    if version == "2.1.0":
        model = "lipsync-2"
        temperature = 1
    elif version == "2.0.5":
        model = "lipsync-2"
        temperature = 0.5
    elif version == "2.0.0":
        model = "lipsync-2"
        temperature = 0
    elif version == "1.9.0":
        model = "lipsync-1.9.0-beta"

    width = int(os.environ.get("WIDTH_TOKEN"))
    height = int(os.environ.get("HEIGHT_TOKEN"))

    POSTHOG_COOKIE = "%7B%22distinct_id%22%3A%223781d6b8-8ef2-4718-b9ea-fb041d135f4b%22%2C%22%24sesid%22%3A%5B1753829914273%2C%2201985861-446b-7114-854f-f50f3c38a7c0%22%2C1753829426283%5D%2C%22%24session_is_sampled%22%3Atrue%2C%22%24epp%22%3Atrue%7D"

    """
    Genera un video de lipsync combinando un video y un audio previamente subidos.

    Args:
        video_asset_id (str): ID del recurso de tipo VIDEO.
        audio_asset_id (str): ID del recurso de tipo AUDIO.
        project_id (str): ID del proyecto en sync.so.

    Returns:
        dict: Respuesta JSON con el ID del trabajo generado.
    """
    import requests

    # URL de la API
    url = "https://api.sync.so/v2/generate"

    # Headers completos (copiados del trace)
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": '"Windows"',
        "x-sync-project-id": project_id,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        "Content-Type": "application/json",
        "sec-ch-ua-mobile": "?0",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f"__Secure-sync.session_token={session_token}; ph_phc_82dxgIiZvuUFV41LErIq8UGCNYmisHq8Fn3a4LGtsYO_posthog={POSTHOG_COOKIE}",
        "Accept-Encoding": "gzip, deflate"
        
    }

    # Cuerpo de la solicitud
    data = {
        "model": model,
        "input": [
            {"type": "video", "assetId": video_asset_id},
            {"type": "audio", "assetId": audio_asset_id}
        ],
        "options": {
            "pads": [0, 5, 0, 0],
            "temperature": 0.5,
            "output_resolution": [width, height],
            "output_format": "mp4",
            "sync_mode": "bounce",
            "model_mode": "emotion",
            "active_speaker_detection": {"auto_detect": False},
            "occlusion_detection_enabled": False
        }
    }

    print("🎬 Generando lipsync...")
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        resultado = response.json()
        print("✅ Lipsync iniciado.")
        #print(f"ID del trabajo: {resultado['id']}")
        return resultado, resultado['id']
    else:
        return None, None


def gen_ava(version):
    # Supongamos que ya tienes estos IDs
    register_lip()
    time.sleep(1)
    create_projects()
    time.sleep(1)
    up_audio("/tmp/audio.mp3")
    time.sleep(1)
    up_video("/tmp/video_f.mp4")
    time.sleep(1)
    session_token = os.environ.get("ACCESS_TOKEN")
    project_id = os.environ.get("PROJECT_ID")
    audio_asset_id = os.environ.get("ASSET_ID_AUDIO")
    video_asset_id = os.environ.get("ASSET_ID_VIDEO")


    # Generar lipsync
    lipsync_job, generation_id = generar_lipsync(video_asset_id, audio_asset_id, project_id, session_token, version)

    if lipsync_job:
      os.environ["GENERATION_ID"] = generation_id
      #print(lipsync_job)

      # === Cargar variables de entorno ===
      project_id = os.environ.get("PROJECT_ID")
      session_token = os.environ.get("ACCESS_TOKEN")

      if not project_id or not session_token:
          raise ValueError("❌ Faltan: PROJECT_ID o ACCESS_TOKEN")

      # === Ejecutar: esperar y obtener URL ===
      final_url = wait_for_completion_and_get_url(project_id, session_token, max_wait=900, check_interval=10)

      # === Si se obtuvo la URL, descargar ===
      if final_url:
          #print(f"\n✅ Video listo: {final_url}")
          print(f"\n✅ Video listo...")
          download_video(final_url, "/tmp/output.mp4")

          # Llama a la función
          generation_id = os.environ.get("GENERATION_ID")
          session_token = os.environ.get("ACCESS_TOKEN")
          resultado = delete_generation(generation_id, session_token)
          if resultado:
            print("✅ Generación eliminada correctamente")

          project_id = os.environ.get("PROJECT_ID")
          session_token = os.environ.get("ACCESS_TOKEN")
          # Llama a la función
          resultado = delete_project(project_id, session_token)

          # Muestra el resultado
          #print(resultado)

      else:
          print("❌ No se pudo obtener la URL del video.")
