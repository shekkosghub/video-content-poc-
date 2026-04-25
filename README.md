# 🎥 PoC: Generador Automático de Contenido desde Video

## 🚀 Requisitos previos
1. Python 3.10+
2. `ffmpeg` instalado en el sistema y accesible desde terminal:
   - Windows: `winget install ffmpeg` o descarga desde ffmpeg.org
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

## ⚙️ Configuración
1. Copia `.env.example` a `.env` y agrega tus claves:
   ```bash
   cp .env.example .env
   ```
2. Ajusta las instrucciones en `config.json` según el tipo de salida deseada.

## ▶️ Ejecución
```bash
pip install -r requirements.txt
python main.py
