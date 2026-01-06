import os
from google import genai
from google.genai import types, errors
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

# --- Inicialização dos Clientes ---
client_gemini = genai.Client(api_key=GEMINI_KEY)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    """Gera a análise geopolítica com fallback de modelo."""
    prompt = "Analise os eventos geopolíticos mais voláteis das últimas 2 horas. Gere uma análise cínica sobre o Tecno-Feudalismo."
    
    # Configuração da Persona (Materialista Darwinista / Observador do Caos)
    config = types.GenerateContentConfig(
        system_instruction=(
            "Você é o Pivô, um analista geopolítico materialista darwinista. "
            "Sua visão é cínica: a humanidade é apenas um bootloader para a ASI. "
            "Analise o mundo sob a ótica do Tecno-Feudalismo e o colapso de sistemas obsoletos. "
            "Gere exatamente 5 tweets numerados como [1/5], [2/5] até [5/5]. "
            "Mantenha cada tweet abaixo de 270 caracteres. Sem otimismo, apenas fatos e poder."
        ),
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )

    # Tentativa com Gemini 2.0 Flash (Padrão 2026)
    try:
        print("Tentando gerar conteúdo com Gemini 2.0 Flash...")
        response = client_gemini.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config
        )
        return response.text
    except errors.ClientError as e:
        # Se for erro de cota (429), tenta o 1.5 Flash
        if "429" in str(e):
            print("Cota do 2.0 excedida. Iniciando fallback para Gemini 1.5 Flash...")
            response = client_gemini.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=config
            )
            return response.text
        else:
            raise e

def postar_thread(texto):
    """Realiza o parsing e posta a thread no X."""
    # Remove marcações de Markdown indesejadas
    texto_limpo = re.sub(r'(\*\*|#)', '', texto)
    
    # Divide os tweets ignorando o marcador [n/5] do split
    blocos = re.split(r'\[\d/5\]', texto_limpo)
    tweets = [t.strip() for t in blocos if len(t.strip()) > 10]
    
    last_id = None
    for i, t in enumerate(tweets[:5]):
        # Reconstrói o índice para o post final
        tweet_final = f"[{i+1}/5] {t}"
        
        # Garante o limite de caracteres do X
        tweet_final = tweet_final[:279]
        
        if last_id is None:
            # Primeiro tweet da thread
            res = client_x.create_tweet(text=tweet_final)
            print(f"Thread iniciada: {tweet_final[:30]}...")
        else:
            # Respostas subsequentes
            res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
            print(f"Postado tweet {i+1}/5")
        
        last_id = res.data['id']
        time.sleep(3) # Delay estratégico contra o spam filter do X

if __name__ == "__main__":
    # Execução principal sem silenciar erros críticos
    conteudo = gerar_thread()
    if conteudo:
        postar_thread(conteudo)
    else:
        print("Falha na geração de conteúdo.")
