import openai
import speech_recognition as sr
import requests
import playsound
import sys
from configparser import ConfigParser

# Config-Datei auslesen
config = ConfigParser()
config.read('ai_config.cfg')

# OpenAI API initialisieren
openai.api_key = config.get('openai', 'api_key')

# User-Name initialisieren
user_name = config.get('username', 'name')

# Recognizer-Objekt und Trigger Variablen
r = sr.Recognizer()
gibson_trigger = "gibson" #gpt-4
luna_trigger = "luna" #gpt-3.5-turbo
stop_trigger = "exit" #beendet das Programm

def get_trigger(text):
    if gibson_trigger in text.lower():
        return gibson_trigger
    elif luna_trigger in text.lower():
        return luna_trigger
    elif stop_trigger in text.lower():
        sys.exit()
    else:
        return None
    
# Sprachsynthese mit Elevenlabs und zwei möglichen Stimmen   
def text_to_speech(response, trigger):
    CHUNK_SIZE = 1024
    if trigger == "luna":
        voice = config.get('voices', 'luna_voice_id')
    elif trigger == "gibson":
        voice = config.get('voices', 'gibson_voice_id')
        
    url = "https://api.elevenlabs.io/v1/text-to-speech/"+voice+"/stream"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config.get('elevenlabs', 'api_key')
    }
    
    data = {
        "text": response,
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
                    trigger = get_trigger(text) #Trigger erkennen
                    if trigger is not None:
                        break
                    else:
                        print("Kein Trigger-Wort. Versuche es noch einmal.")
                except Exception as e:
                    print("Fehler bei der Spracherkennung: {0}".format(e))
                    continue
                    
            print("Du kannst den Prompt einfach laut aussprechen. Ich höre dir zu.")
            text_to_speech('Hallo '+user_name+'. Hier ist '+trigger+'.',trigger)
            
            audio = r.listen(source)
            
            try:
                user_prompt = r.recognize_google(audio, language='de-de')
                print(f"Du: {user_prompt}")
            except Exception as e:
                print("Fehler bei der Spracherkennung: {0}".format(e))
                continue
            
            if trigger == gibson_trigger:
                # Gibson - GPT-4 API
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content":
                        config.get('roles', 'gibson')+" Dein Name ist Gibson. Beantworte alle Fragen in dieser Rolle und rede mich dabei mit "+user_name+" an."},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    frequency_penalty=0.3,
                    presence_penalty=0.3,
                    n=1,
                    stop=["\nDu:"],
                )
                
                ai_response = response["choices"][0]["message"]["content"]

            else:
                # Luna - GPT-3.5-turbo API
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content":
                        config.get('roles', 'luna')+" Dein Name ist Luna. Beantworte alle Fragen in dieser Rolle und rede mich dabei mit "+user_name+" an."},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.8,
                    max_tokens=2048,
                    frequency_penalty=0.3,
                    presence_penalty=0.3,
                    n=1,
                    stop=["\nDu:"],
                )

                ai_response = response["choices"][0]["message"]["content"]
                
        print(f"{trigger}:", ai_response)
        text_to_speech(ai_response, trigger) # Sprachausgabe der AIs, je nach Trigger-Wort, Gibson oder Luna
if __name__ == "__main__":
    main()                 
