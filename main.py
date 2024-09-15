import gradio as gr
import whisper
from translate import Translator
from dotenv import dotenv_values
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Cargamos configuración de variables de entorno
config = dotenv_values(".env")
ELEVENLABS_API_KEY = config["ELEVENLABS_API_KEY"]

# Función principal: transcribir, traducir y generar audios en varios idiomas
def translator(audio_file):
    transcription = transcribe_audio(audio_file)
    translations = translate_text(transcription)
    audio_files = generate_translated_audio(translations)
    
    return audio_files
    
# 1. Transcribir el audio a texto usando Whisper
# Usamos https://github.com/openai/whisper
# Alternativa https://www.assemblyai.com/

def transcribe_audio(audio_file):    
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file, language = "Spanish", fp16 = False)
        transcription = result["text"]
        print(f"Texto original: {transcription}")
        return transcription
    except Exception as e:
        raise gr.Error(
            f"Error al transcribir el audio: {str(e)}"
        )
    
    
# 2. Traducir el texto a varios idiomas usando Translate
# Usamos https://github.com/terryyin/translate-python
# https://pypi.org/project/translate/

def translate_text(transcription):
    languages = ["en", "it", "fr", "pt"]
    translations = {}
        
    try:
        for lang in languages:
            translator = Translator(from_lang = "es", to_lang = lang)
            translations[lang]  = translator.translate(transcription)
            print(f"Texto traducido a {lang}: {translations[lang]}")
        return translations
    except Exception as e:
        raise gr.Error(
            f"Error al traducir el texto: {str(e)}"
        )

    
# 3. Generar el audio traducido usando ElevenLabs
# Usamos Elevenlabs IO: https://elevenlabs.io/docs/api-reference/getting-started
# https://github.com/elevenlabs/elevenlabs-python
# Debemos registrarnos y generar el API Key, la cual va almacenada en el archivo .env del proyecto

def generate_translated_audio(translations):
    audio_paths = []
    
    try:
        for lang, text in translations.items():
            audio_path = text_to_speech(text, lang)
            audio_paths.append(audio_path)
        return audio_paths
    except Exception as e:
        raise gr.Error(f"Error al generar audios traducidos: {str(e)}")

# Generar el audio traducido con ElevenLabs
# Usamos Text-to-Speech
# https://github.com/elevenlabs/elevenlabs-examples/blob/main/examples/text-to-speech/python/text_to_speech_file.py
# Voices: https://elevenlabs.io/app/voice-lab

def text_to_speech(text: str, language: str) -> str:
    
    try:
        client = ElevenLabs(
            api_key = ELEVENLABS_API_KEY
        )
        
        response = client.text_to_speech.convert(
            voice_id="z9fAnlkpzviPz146aGWa",  # Glinda
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2",  # use the turbo model for low latency
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )
    
        save_file_path = f"audios/{language}.mp3"
        
        # Guardamos el fichero
        with open(save_file_path, "wb") as f: # Formato Escritura y Binario
            for chunk in response:
                if chunk:
                    f.write(chunk)
        
        print(f"Audio traducido guardado en: {save_file_path}")

        # Retornamos la ruta donde se almacenó el fichero traducido
        return save_file_path
    
    except Exception as e:
        raise gr.Error(
            f"Error al guardar audio traducido: {str(e)}"
        )
    
 
# Configuración de la interfaz de Gradio   
web = gr.Interface(
    fn = translator,
    inputs = gr.Audio(
        sources = ["microphone"],
        type = "filepath",
        label = "Español"
        ),
    outputs = [
        gr.Audio(label="Inglés"),
        gr.Audio(label="Italiano"),
        gr.Audio(label="Francés"),
        gr.Audio(label="Portugués"),
        ],
    title = "Traductor de voz",
    description = "Traductor de voz con IA a varios idiomas"
)

web.launch()