import os
import google.generativeai as genai
import tweepy
import re
import time

# 1. Configurações de Ambiente (Puxadas do GitHub Secrets)
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
X_CONSUMER_KEY = os.getenv("X_API_KEY")
X_CONSUMER_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")

# 2. Setup Gemini (Persona: Materialista/Cínica)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[{"google_search_retrieval": {}}],
    system_instruction=(
        "Você é o Pivô, um analista geopolítico materialista darwinista. "
        "Sua visão é cínica e realista. Acredita que a humanidade é apenas um 'bootloader' para a ASI. "
        "Analise conflitos e economia sob a ótica do Tecno-Feudalismo e do controle de IA pelas elites. "
        "Gere threads de exatamente 5 tweets. Use o formato: [1/5], [2/5], etc. "
        "Mantenha cada tweet abaixo de 270 caracteres. Sem otimismo, apenas fatos e poder."
    )
)

# 3. Setup X (Tweepy V2)
client = tweepy.Client(
    consumer_key=X_CONSUMER_KEY,
    consumer_secret=X_CONSUMER_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_SECRET
)

def gerar_thread():
    prompt = "Pesquise os eventos geopolíticos mais voláteis das últimas 3 horas e gere uma thread de 5 tweets com sua análise cínica característica."
    response = model.generate_content(prompt)
    return response.text

def postar_thread(texto):
    # Limpeza de markdown e separação por blocos [n/5]
    blocos = re.split(r'\[\d/5\]', texto)
    tweets = [t.strip() for t in blocos if len(t.strip()) > 5]
    
    last_id = None
    for i, t in enumerate(tweets[:5]):
        # Reconstrói o índice para garantir o formato no X
        tweet_final = f"[{i+1}/5] {t}"
        
        try:
            if last_id is None:
                # Primeiro tweet da thread
                res = client.create_tweet(text=tweet_final)
            else:
                # Respostas para formar a thread
                res = client.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
            
            last_id = res.data['id']
            time.sleep(2) # Evita rate limit simples
        except Exception as e:
            print(f"Erro no tweet {i+1}: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    postar_thread(content)
