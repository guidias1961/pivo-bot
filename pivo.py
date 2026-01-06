import os
from google import genai
from google.genai import types
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
    """Gera a análise usando o 1.5-flash como primário para evitar o erro de cota 0."""
    prompt = "Analise os eventos geopolíticos mais críticos e voláteis das últimas 3 horas. Gere uma análise cínica sobre o Tecno-Feudalismo."
    
    # Configuração da Persona (Materialista Darwinista / Observador do Caos)
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é o Pivô, um analista geopolítico materialista darwinista. "
            "Sua visão é cínica: a humanidade é apenas um bootloader para a ASI. "
            "Analise o mundo sob a ótica do Tecno-Feudalismo e o colapso de sistemas obsoletos. "
            "Gere exatamente 5 tweets numerados como [1/5], [2/5] até [5/5]. "
            "Mantenha cada tweet abaixo de 270 caracteres. Sem otimismo."
        ),
        # Removemos o Grounding temporariamente para garantir que o 404 suma no plano Free
        tools=[] 
    )

    print("Iniciando geração com Gemini 1.5 Flash (Resilience Mode)...")
    # Chamada direta ao 1.5 para ignorar o 429 do 2.0
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
        config=config
    )
    return response.text

def postar_thread(texto):
    """Realiza o parsing e posta a thread no X."""
    # Limpeza de markdown
    texto_limpo = re.sub(r'(\*\*|#)', '', texto)
    
    # Divide os tweets
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
            time.sleep(3)
        except Exception as e:
            print(f"Erro no tweet {i+1}: {e}")

if __name__ == "__main__":
    # Execução direta para capturar erros no log do GitHub
    content = gerar_thread()
    if content:
        postar_thread(content)
