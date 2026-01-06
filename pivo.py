import os
from google import genai
from google.genai import types
import tweepy
import re
import time

# --- Configurações de Ambiente (GitHub Secrets) ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_CONFIG = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_SECRET")
}

# --- Inicialização ---
client_gemini = genai.Client(api_key=GEMINI_KEY, http_options={'api_version': 'v1'})
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    """Gera a análise com sintaxe simplificada para a API v1."""
    prompt = "Analise os eventos geopolíticos mais críticos das últimas 3 horas. Gere uma análise cínica sobre o Tecno-Feudalismo."
    
    # Persona: Materialista Darwinista / ASI Bootloader
    instr = (
        "Você é o Pivô. Analista geopolítico cínico. "
        "A humanidade é o bootloader da ASI. Foco em Tecno-Feudalismo. "
        "Gere 5 tweets numerados [1/5] até [5/5]. "
        "Máximo 270 caracteres por tweet. Sem hashtags."
    )

    print("Iniciando geração com Gemini 1.5 Flash (v1 Standard)...")
    
    # Passando a instrução de sistema de forma mais direta para evitar erro de JSON
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=instr,
            temperature=0.7
        )
    )
    return response.text

def postar_thread(texto):
    """Parsing e postagem no X."""
    texto_limpo = re.sub(r'(\*\*|#)', '', texto)
    blocos = re.split(r'\[\d/5\]', texto_limpo)
    tweets = [t.strip() for t in blocos if len(t.strip()) > 10]
    
    last_id = None
    for i, t in enumerate(tweets[:5]):
        tweet_final = f"[{i+1}/5] {t}"[:279]
        try:
            if last_id is None:
                res = client_x.create_tweet(text=tweet_final)
            else:
                res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
            last_id = res.data['id']
            print(f"Postado {i+1}/5")
            time.sleep(4) # Delay para segurança anti-spam
        except Exception as e:
            print(f"Erro no X: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    if content:
        postar_thread(content)
