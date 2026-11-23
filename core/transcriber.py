# import whisper
# import os
# WHISPER_MODEL=os.getenv("WHISPER_MODEL","small")

# _model=None
# def load_model():
#     global _model
#     if _model is None:
#         print(f"loading model ...")
#         _model=whisper.load_model(WHISPER_MODEL)
#         print("Whisper model loaded successfully")

#     return  _model

# def transcribe_chunk(chunk_path:str,translate:bool=False)->str:
#     model=load_model()
#     task="translate" if translate else "transcribe"
#     result=model.transcribe(chunk_path,task=task)

#     return result["text"]

     
# def transcribe_all(chunks:list[str],translate:bool=False)->str:
#     """
#     Transcribe all chunks and return the combined text.
#     """
#     transcribed_text = ""
#     for chunk_path in chunks:
#         print(f"Transcribing chunk: {chunk_path}")
#         text = transcribe_chunk(chunk_path,translate)
#         transcribed_text += text + " "
#     return transcribed_text.strip()



import whisper
import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

_model = None


def load_model():
    global _model

    if _model is None:
        print("Loading Whisper model...")
        _model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully!")

    return _model


def transcribe_chunk(
    chunk_path: str,
    language: str = "english",
    translate: bool = False
) -> str:

    model = load_model()

    task = "translate" if translate else "transcribe"

    # English: explicitly select English
    # Hinglish: allow Whisper to detect the spoken language
    whisper_language = "en" if language == "english" else None

    result = model.transcribe(
        chunk_path,
        task=task,
        language=whisper_language,
        fp16=False
    )

    return result["text"]


def transcribe_all(
    chunks: list[str],
    language: str = "english",
    translate: bool = False
) -> str:
    """
    Transcribe all audio chunks and return combined text.
    """

    transcribed_text = ""

    for i, chunk_path in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}/{len(chunks)}...")

        text = transcribe_chunk(
            chunk_path,
            language=language,
            translate=translate
        )

        transcribed_text += text + " "

    return transcribed_text.strip()
