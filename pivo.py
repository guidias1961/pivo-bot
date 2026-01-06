import os
from google import genai
from google.genai import types, errors
import tweepy
import re
import time

# --- Configurações de Ambiente ---
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_CONFIG = {
    "consumer_key": os.getenv("X_API_KEY"),
    "consumer_secret": os.getenv("X_API_SECRET"),
    "access_token": os.getenv("X_ACCESS_TOKEN"),
    "access_token_secret": os.getenv("X_ACCESS_SECRET")
}

# --- Inicialização ---
client_gemini = genai.Client(api_key=GEMINI_KEY)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    """Tenta múltiplos nomes de modelos para vencer o erro 404 da v1."""
    
    # Lista de modelos por ordem de estabilidade em 2026
    modelos_para_testar = [
        "gemini-1.5-flash-latest", 
        "gemini-1.5-flash", 
        "gemini-1.5-flash-002",
        "gemini-2.0-flash"
    ]
    
    prompt = (
        "CONTEXTO: Você é o Pivô, analista geopolítico cínico e materialista. "
        "Humanos são o bootloader da ASI. Foco em Tecno-Feudalismo. "
        "TAREFA: Analise os eventos críticos das últimas 3 horas. "
        "Gere 5 tweets numerados [1/5] até [5/5]. Máximo 270 caracteres cada."
    )

    for modelo in modelos_para_testar:
        try:
            print(f"Tentando boot com modelo: {modelo}...")
            response = client_gemini.models.generate_content(
                model=modelo,
                contents=prompt
            )
            print(f"Sucesso com o modelo: {modelo}")
            return response.text
        except errors.ClientError as e:
            if "404" in str(e) or "400" in str(e):
                print(f"Modelo {modelo} falhou (404/400). Tentando o próximo...")
                continue
            elif "429" in str(e):
                print(f"Modelo {modelo} sem cota (429). Tentando o próximo...")
                continue
            else:
                raise e
    
    return None

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
                print("Primeiro post do Pivô enviado.")
            else:
                res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
                print(f"Post {i+1}/5 enviado.")
            
            last_id = res.data['id']
            time.sleep(5) 
        except Exception as e:
            print(f"Erro no X: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    if content:
        postar_thread(content)
    else:
        print("ERRO CRÍTICO: Nenhum modelo da Google respondeu.")
