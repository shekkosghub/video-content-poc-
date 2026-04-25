import os
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

CONFIG_FILE = "config.json"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_audio(video_path: str, audio_path: str) -> bool:
    """Extrae audio en 16kHz mono (óptimo para Whisper/DeepSeek) usando ffmpeg"""
    cmd = [
        "ffmpeg", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "16000", "-ac", "1",
        audio_path, "-y"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio usando Whisper API (OpenAI compatible)"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ Falta OPENAI_API_KEY en el archivo .env")
    
    client = OpenAI(api_key=api_key)
    with open(audio_path, "rb") as f:
        response = client.audio.transcriptions.create(model="whisper-1", file=f)
    return response.text.strip()

def generate_content(transcription: str, config: dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("⚠️ Falta OPENAI_API_KEY en el archivo .env")
    
    # Un solo cliente OpenAI para transcripción y generación
    client = OpenAI(api_key=api_key)
    
    prompt = (
        f"Transcripción del video:\n---\n{transcription}\n---\n\n"
        f"Instrucciones: {config['instructions']}\n"
        f"Idioma de salida: {config.get('language', 'es')}"
    )
    
    response = client.chat.completions.create(
        model=config.get("api_model", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Eres un asistente experto en síntesis y estructuración de contenido audiovisual."},
            {"role": "user", "content": prompt}
        ],
        temperature=config.get("temperature", 0.3),
        max_tokens=config.get("max_tokens", 2000)
    )
    return response.choices[0].message.content.strip()

def main():
    video_path = input("📁 Ingresa la ruta del video: ").strip()
    if not Path(video_path).exists():
        print("❌ Error: El archivo no existe. Verifica la ruta.")
        return

    # Cargar configuración
    if not Path(CONFIG_FILE).exists():
        print("❌ Error: No se encontró config.json")
        return
    
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)

    audio_path = str(OUTPUT_DIR / "temp_audio.wav")
    output_path = str(OUTPUT_DIR / "resultado.md")

    try:
        print("🎬 1/3 Extrayendo audio...")
        if not extract_audio(video_path, audio_path):
            print("❌ Error en ffmpeg. Asegúrate de tenerlo instalado y en el PATH.")
            return

        print("🎤 2/3 Transcribiendo audio...")
        transcription = transcribe_audio(audio_path)

        print("🤖 3/3 Generando contenido con DeepSeek...")
        content = generate_content(transcription, config)

        # Guardar resultado
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Proceso completado. Resultado guardado en: {output_path}")
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")
    finally:
        # Limpieza temporal
        if Path(audio_path).exists():
            os.remove(audio_path)

if __name__ == "__main__":
    main()
