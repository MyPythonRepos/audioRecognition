import argparse
import os

from pydub import AudioSegment
from pydub.utils import make_chunks
import speech_recognition as sr

SUPPORTED_FORMATS = {
    ".wav": "wav",
    ".mp3": "mp3",
    ".ogg": "ogg",
    ".flac": "flac",
    ".aac": "aac",
    ".wma": "wma",
    ".m4a": "m4a",
    ".webm": "webm",
}


def load_audio(filepath):
    """Carga un fichero de audio en cualquier formato soportado y devuelve un AudioSegment."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Formato '{ext}' no soportado. Formatos válidos: {', '.join(SUPPORTED_FORMATS)}"
        )
    fmt = SUPPORTED_FORMATS[ext]
    return AudioSegment.from_file(filepath, format=fmt)


def split_audio(audio, min_per_split, output_dir="files"):
    """Divide un AudioSegment en chunks de min_per_split minutos y los exporta como WAV."""
    os.makedirs(output_dir, exist_ok=True)
    chunk_length_ms = min_per_split * 60 * 1000
    chunks = make_chunks(audio, chunk_length_ms)
    exported = []
    for i, chunk in enumerate(chunks):
        chunk_name = "{0:>3}.wav".format(i)
        chunk_path = os.path.join(output_dir, chunk_name)
        print("exporting", chunk_name)
        chunk.export(chunk_path, format="wav")
        exported.append(chunk_path)
    print('All split successfully')
    return exported


def transcribe_files(input_dir="files", output_file="texto.txt", language="es-ES"):
    """Transcribe todos los ficheros .wav de input_dir y escribe el resultado en output_file."""
    r = sr.Recognizer()
    lines = []
    wav_files = sorted(f for f in os.listdir(input_dir) if f.lower().endswith(".wav"))
    for f in wav_files:
        filepath = os.path.join(input_dir, f)
        with sr.AudioFile(filepath) as source:
            info_audio = r.record(source)
            try:
                texto = r.recognize_google(info_audio, language=language)
            except sr.UnknownValueError:
                texto = "[inaudible]"
            except sr.RequestError as e:
                texto = f"[error: {e}]"
            lines.append(texto)
            print(texto)
    with open(output_file, "w", encoding="utf-8") as archivo:
        for line in lines:
            archivo.write(line + '\n')
    return lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Transcribe un fichero de audio a texto."
    )
    parser.add_argument(
        "input", help="Fichero de audio de entrada (wav, mp3, ogg, flac, aac, wma, m4a, webm)"
    )
    parser.add_argument(
        "-o", "--output", default="texto.txt",
        help="Fichero de texto de salida (por defecto: texto.txt)"
    )
    parser.add_argument(
        "-c", "--chunks-dir", default="files",
        help="Directorio para los fragmentos temporales (por defecto: files)"
    )
    parser.add_argument(
        "-m", "--minutes", type=float, default=1,
        help="Duración en minutos de cada fragmento (por defecto: 1)"
    )
    parser.add_argument(
        "-l", "--language", default="es-ES",
        help="Código de idioma para el reconocimiento (por defecto: es-ES)"
    )
    args = parser.parse_args()

    audio = load_audio(args.input)
    split_audio(audio, min_per_split=args.minutes, output_dir=args.chunks_dir)
    transcribe_files(
        input_dir=args.chunks_dir,
        output_file=args.output,
        language=args.language,
    )
