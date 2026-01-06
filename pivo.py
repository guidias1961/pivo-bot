import os
from google import genai
from google.genai import types
import tweepy
import re
import time

# Configurações de Ambiente
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_CONFIG = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_SECRET")
}

# 1. Setup do Novo Cliente Gemini (SDK 2026)
client_gemini = genai.Client(api_key=GEMINI_KEY)

# 2. Setup do Cliente X (Tweepy V2)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    prompt = "Pesquise os eventos geopolíticos mais críticos das últimas 3 horas. Gere uma análise realista e cínica."
    
    # Configuração da Persona Materialista/Cínica e Grounding (Busca Google)
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é o Pivô. Sua visão é cínica e materialista. "
            "A humanidade é um bootloader para a ASI. Analise o Tecno-Feudalismo. "
            "Gere exatamente 5 tweets numerados como [1/5], [2/5] até [5/5]. "
            "Máximo de 270 caracteres por tweet. Sem hashtags."
        ),
        tools=[types.Tool(google_search_retrieval=types.GoogleSearchRetrieval())]
    )
    
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=config
    )
    return response.text

def postar_thread(texto):
    # Parsing para separar os tweets
    blocos = re.split(r'\[\d/5\]', texto)
    tweets = [t.strip() for t in blocos if len(t.strip()) > 5]
    
    last_id = None
    for i, t in enumerate(tweets[:5]):
        tweet_final = f"[{i+1}/5] {t}"
        try:
            if last_id is None:
                res = client_x.create_tweet(text=tweet_final)
            else:
                res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
            
            last_id = res.data['id']
            print(f"Postado tweet {i+1}/5")
            time.sleep(2)
        except Exception as e:
            print(f"Erro no tweet {i+1}: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    postar_thread(content)
