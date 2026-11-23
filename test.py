from utils.audioprocessor import process_input
from core.transcriber import transcribe_all

source="https://youtu.be/Ty8gcCKuwNI?si=8kXaRR3icyWwBjww"
chunks=process_input(source)
print(transcribe_all(chunks))