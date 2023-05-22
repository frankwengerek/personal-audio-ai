import openai

class AI:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key
        
    def ask(self, version, messages = []):
        if version == "gpt-3.5-turbo":
            return self.ask_gpt_3_5_turbo(messages)          
        else:
            return self.ask_gpt_4(messages)
        
    def ask_gpt_3_5_turbo(self, messages = []):
        return openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=2048,
            frequency_penalty=0.3,
            presence_penalty=0.3,
            n=1,
            stop=["\nDu:"],
        )
        
    def ask_gpt_4(self, messages = []):
        return openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            frequency_penalty=0.3,
            presence_penalty=0.3,
            n=1,
            stop=["\nDu:"],
        )
    

