import os

from pydub import AudioSegment
import math
from pydub.utils import make_chunks
import speech_recognition as sr


def multiple_split(audio, min_per_split):
    chunk_length_ms = min_per_split * 60 * 1000
    chunks = make_chunks(audio, chunk_length_ms)
    for i, chunk in enumerate(chunks):
        chunk_name = "{0:>3}.wav".format(i)
        print("exporting", chunk_name)
        chunk.export("files/" + chunk_name, format="wav")
    print('All splited successfully')


if __name__ == '__main__':
    audio = AudioSegment.from_wav("audiofile.wav")
    # multiple_split(audio, min_per_split=1)
    archivo = open("texto.txt", "a+")
    r = sr.Recognizer()
    path = "./files"
    for f in sorted(os.listdir(path)):
        with sr.AudioFile(path + "/" + f) as source:
            info_audio = r.record(source)
            texto = r.recognize_google(info_audio, language='es-ES')
            archivo.write(texto+'\n')
            print(texto)
    archivo.close()
