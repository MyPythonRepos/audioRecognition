# Audio Recognition

Script de Python que transcribe ficheros de audio a texto utilizando la API de Google Speech Recognition.

## Formatos soportados

`.wav` `.mp3` `.ogg` `.flac` `.aac` `.wma` `.m4a` `.webm`

## Requisitos

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/) instalado y disponible en el `PATH`

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py <fichero_audio> [opciones]
```

### Opciones

| Argumento | Descripción | Por defecto |
| --- | --- | --- |
| `input` | Fichero de audio de entrada | *obligatorio* |
| `-o, --output` | Fichero de texto de salida | `texto.txt` |
| `-c, --chunks-dir` | Directorio para fragmentos temporales | `files` |
| `-m, --minutes` | Duración de cada fragmento (minutos) | `1` |
| `-l, --language` | Código de idioma para el reconocimiento | `es-ES` |

### Ejemplos

```bash
# Transcripción básica
python main.py entrevista.mp3

# Especificar fichero de salida e idioma inglés
python main.py podcast.flac -o transcripcion.txt -l en-US

# Fragmentos de 2 minutos en un directorio personalizado
python main.py charla.ogg -m 2 -c temp_chunks
```

## Docker

### Construir la imagen

```bash
docker build -t audio-recognition .
```

### Ejecutar

```bash
docker run --rm \
  -v /ruta/a/audio.mp3:/app/audio.mp3 \
  -v /ruta/salida:/app/output \
  audio-recognition audio.mp3 -o /app/output/texto.txt
```

## Funcionamiento

1. **Carga** el fichero de audio en cualquier formato soportado (vía `pydub` + `ffmpeg`).
2. **Divide** el audio en fragmentos de duración configurable y los exporta como WAV en el directorio de chunks.
3. **Transcribe** cada fragmento usando Google Speech Recognition y escribe el texto resultante en el fichero de salida.

Los fragmentos no reconocibles se marcan como `[inaudible]`. Los errores de conexión se registran como `[error: ...]`.

## Tests

```bash
pip install pytest
python -m pytest test_main.py -v
```
