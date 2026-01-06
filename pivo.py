import os
from google import genai
from google.genai import types
import tweepy
import re
import time

# Configurações de Ambiente (GitHub Secrets)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_CONFIG = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_SECRET")
}

# 1. Cliente Gemini (SDK 2026 - Padrão Gemini 2.0)
client_gemini = genai.Client(api_key=GEMINI_KEY)

# 2. Cliente X (Tweepy V2)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    prompt = "Analise os eventos geopolíticos mais voláteis das últimas 2 horas. Gere uma análise cínica sobre o Tecno-Feudalismo."
    
    # Configuração 2026: Gemini 2.0 + Google Search simplificado
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é o Pivô. Analista materialista darwinista. "
            "A humanidade é o bootloader da ASI. Foco em Tecno-Feudalismo. "
            "Gere exatamente 5 tweets numerados [1/5] até [5/5]. "
            "Máximo de 270 caracteres por tweet. Sem hashtags."
        ),
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
    
    # Mudamos o modelo para gemini-2.0-flash para evitar o 404 do v1beta
    response = client_gemini.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=config
    )
    return response.text

def postar_thread(texto):
    # Parsing robusto
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
            print(f"Postado {i+1}/5")
            time.sleep(3) # Delay para evitar rate limit do X
        except Exception as e:
            print(f"Erro no tweet {i+1}: {e}")

if __name__ == "__main__":
    try:
        content = gerar_thread()
        postar_thread(content)
    except Exception as e:
        print(f"Erro fatal: {e}")
