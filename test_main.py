import os
import tempfile
import struct
import wave

import pytest
from unittest.mock import patch, MagicMock
from pydub import AudioSegment

from main import split_audio, transcribe_files, load_audio, SUPPORTED_FORMATS


def create_silent_wav(path, duration_ms=1000, sample_rate=16000):
    """Crea un fichero WAV silencioso de duración dada."""
    n_samples = int(sample_rate * duration_ms / 1000)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * n_samples, *([0] * n_samples)))


class TestLoadAudio:
    def test_loads_wav(self, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        create_silent_wav(wav_path)
        audio = load_audio(wav_path)
        assert len(audio) > 0

    def test_unsupported_format_raises(self, tmp_path):
        txt_path = str(tmp_path / "test.txt")
        with open(txt_path, "w") as f:
            f.write("not audio")
        with pytest.raises(ValueError, match="no soportado"):
            load_audio(txt_path)

    def test_all_supported_extensions_recognized(self):
        expected = {".wav", ".mp3", ".ogg", ".flac", ".aac", ".wma", ".m4a", ".webm"}
        assert set(SUPPORTED_FORMATS.keys()) == expected


class TestSplitAudio:
    def test_creates_output_directory(self, tmp_path):
        output_dir = str(tmp_path / "output")
        audio = AudioSegment.silent(duration=3000)  # 3 seconds
        result = split_audio(audio, min_per_split=1, output_dir=output_dir)
        assert os.path.isdir(output_dir)
        assert len(result) >= 1

    def test_exports_wav_files(self, tmp_path):
        output_dir = str(tmp_path / "chunks")
        audio = AudioSegment.silent(duration=120_000)  # 2 minutes
        result = split_audio(audio, min_per_split=1, output_dir=output_dir)
        assert len(result) == 2
        for path in result:
            assert os.path.isfile(path)
            assert path.endswith(".wav")

    def test_single_chunk_when_audio_shorter_than_split(self, tmp_path):
        output_dir = str(tmp_path / "chunks")
        audio = AudioSegment.silent(duration=30_000)  # 30 seconds
        result = split_audio(audio, min_per_split=1, output_dir=output_dir)
        assert len(result) == 1

    def test_existing_output_dir_no_error(self, tmp_path):
        output_dir = str(tmp_path / "existing")
        os.makedirs(output_dir)
        audio = AudioSegment.silent(duration=1000)
        result = split_audio(audio, min_per_split=1, output_dir=output_dir)
        assert len(result) >= 1


class TestTranscribeFiles:
    @patch("main.sr.Recognizer")
    def test_transcribes_wav_files(self, mock_recognizer_cls, tmp_path):
        # Crear ficheros WAV de prueba
        input_dir = str(tmp_path / "input")
        os.makedirs(input_dir)
        create_silent_wav(os.path.join(input_dir, "  0.wav"))
        create_silent_wav(os.path.join(input_dir, "  1.wav"))

        output_file = str(tmp_path / "resultado.txt")

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = ["texto uno", "texto dos"]
        mock_recognizer_cls.return_value = mock_recognizer

        result = transcribe_files(input_dir=input_dir, output_file=output_file)

        assert result == ["texto uno", "texto dos"]
        with open(output_file, encoding="utf-8") as f:
            content = f.read()
        assert "texto uno\n" in content
        assert "texto dos\n" in content

    @patch("main.sr.Recognizer")
    def test_handles_unknown_value_error(self, mock_recognizer_cls, tmp_path):
        import speech_recognition as sr

        input_dir = str(tmp_path / "input")
        os.makedirs(input_dir)
        create_silent_wav(os.path.join(input_dir, "  0.wav"))

        output_file = str(tmp_path / "resultado.txt")

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = sr.UnknownValueError()
        mock_recognizer_cls.return_value = mock_recognizer

        result = transcribe_files(input_dir=input_dir, output_file=output_file)

        assert result == ["[inaudible]"]

    @patch("main.sr.Recognizer")
    def test_handles_request_error(self, mock_recognizer_cls, tmp_path):
        import speech_recognition as sr

        input_dir = str(tmp_path / "input")
        os.makedirs(input_dir)
        create_silent_wav(os.path.join(input_dir, "  0.wav"))

        output_file = str(tmp_path / "resultado.txt")

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.side_effect = sr.RequestError("no connection")
        mock_recognizer_cls.return_value = mock_recognizer

        result = transcribe_files(input_dir=input_dir, output_file=output_file)

        assert len(result) == 1
        assert "[error:" in result[0]

    @patch("main.sr.Recognizer")
    def test_ignores_non_wav_files(self, mock_recognizer_cls, tmp_path):
        input_dir = str(tmp_path / "input")
        os.makedirs(input_dir)
        create_silent_wav(os.path.join(input_dir, "  0.wav"))
        # Crear un fichero no-wav
        with open(os.path.join(input_dir, "readme.txt"), "w") as f:
            f.write("ignore me")

        output_file = str(tmp_path / "resultado.txt")

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "solo uno"
        mock_recognizer_cls.return_value = mock_recognizer

        result = transcribe_files(input_dir=input_dir, output_file=output_file)

        assert len(result) == 1
        assert mock_recognizer.recognize_google.call_count == 1

    @patch("main.sr.Recognizer")
    def test_output_file_uses_utf8(self, mock_recognizer_cls, tmp_path):
        input_dir = str(tmp_path / "input")
        os.makedirs(input_dir)
        create_silent_wav(os.path.join(input_dir, "  0.wav"))

        output_file = str(tmp_path / "resultado.txt")

        mock_recognizer = MagicMock()
        mock_recognizer.recognize_google.return_value = "café con señal"
        mock_recognizer_cls.return_value = mock_recognizer

        transcribe_files(input_dir=input_dir, output_file=output_file)

        with open(output_file, encoding="utf-8") as f:
            assert "café con señal" in f.read()
