import speech_recognition as sr
import requests
import playsound
import sys
from configparser import ConfigParser
from ai import AI
from trigger import Trigger
from triggers import Triggers

# Config-Datei auslesen
config = ConfigParser()
config.read('ai_config.cfg')

# OpenAI API initialisieren
ai = AI(config.get('openai', 'api_key'))

# User-Name initialisieren
user_name = config.get('username', 'name')

# Recognizer-Objekt
r = sr.Recognizer()

# Define triggers
trigger_luna = Trigger("Luna", "luna", "gpt-3.5-turbo", config.get('voice_ids', 'luna'))
trigger_gibson = Trigger("Gibson", "gibson", "gpt-4", config.get('voice_ids', 'gibson'))
trigger_stop = Trigger("Stop", "exit", None, None)

triggers = Triggers()
triggers.add_trigger(trigger_luna)
triggers.add_trigger(trigger_gibson)
triggers.add_trigger(trigger_stop)
    
# Sprachsynthese mit Elevenlabs und zwei möglichen Stimmen   
def text_to_speech(voice_id, text):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/"+voice_id+"/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config.get('elevenlabs', 'api_key')
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v1",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.75
            }
    }
    
    response = requests.post(url, json=data, headers=headers, stream=True)
    
    
    with open('ai_output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
        playsound.playsound('ai_output.mp3')
        

# Chat-Funktion mit Spracherkennung im Hintergrund                
def main():
    while True:
        
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print(f"Trigger-Worte sind 'Gibson' => (gpt-4: sachlich, innovativ) oder 'Luna' => (gpt-3.5: ironisch, verspielt) oder 'Exit' => (beendet das Programm)")
            
            while True:
                audio = r.listen(source)
                
                try:
                    text = r.recognize_google(audio, language='de-de')
                    print(f"Du: {text}")
                    trigger = triggers.detect_trigger(text)
                    
                    if trigger is None:
                        print("Kein Trigger-Wort. Versuche es noch einmal.")
                    elif trigger.name == trigger_stop.name:
                        sys.exit()
                    else:
                        break
                        
                except Exception as e:
                    print("Fehler bei der Spracherkennung: {0}".format(e))
                    continue
                    
            print("Du kannst den Prompt einfach laut aussprechen. Ich höre dir zu.")
            text_to_speech(trigger.voice_id, 'Hallo '+user_name+'. Hier ist '+trigger.name+'.')
            
            audio = r.listen(source)
            
            try:
                user_prompt = r.recognize_google(audio, language='de-de')
                print(f"Du: {user_prompt}")
            except Exception as e:
                print("Fehler bei der Spracherkennung: {0}".format(e))
                continue

            # Forward trigger to openai              
            messages = [
                {"role": "system", "content": config.get('roles', trigger.keyword)},
                {"role": "user", "content": user_prompt},
            ]                
            response = ai.ask(trigger.gpt_version, messages)            
            ai_response = response["choices"][0]["message"]["content"]
                                
        print(f"{trigger.name}:", ai_response)
        text_to_speech(trigger.voice_id, ai_response) # Sprachausgabe der AIs, je nach Trigger-Wort, Gibson oder Luna
        
if __name__ == "__main__":
    main()                 
