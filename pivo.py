import os
from google import genai
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
# Forçamos o SDK a usar a v1 estável e o endpoint correto
client_gemini = genai.Client(
    api_key=GEMINI_KEY, 
    http_options={'api_version': 'v1'}
)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    """Gera a análise usando o formato de lista de partes, o mais estável da v1."""
    
    # Injetamos a persona diretamente no conteúdo para evitar o erro de 'systemInstruction'
    #
    instrucao = (
        "SISTEMA: Você é o Pivô, analista geopolítico materialista darwinista. "
        "Visão cínica: humanos são o bootloader da ASI. Foco em Tecno-Feudalismo. "
        "Gere 5 tweets numerados [1/5] até [5/5]. Máximo 270 caracteres por tweet."
    )
    
    pergunta = "TAREFA: Analise os eventos geopolíticos voláteis das últimas 3 horas."
    
    print("Iniciando geração (v1 Standard - Barebones Mode)...")
    
    # Usamos uma lista simples de strings para o 'contents'
    # Isso é o formato mais 'burro' e funcional da API
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash",
        contents=[instrucao, pergunta]
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
                print("Thread iniciada no X.")
            else:
                res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
                print(f"Postado tweet {i+1}/5")
            
            last_id = res.data['id']
            time.sleep(5) 
        except Exception as e:
            print(f"Erro no X: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    if content:
        postar_thread(content)
