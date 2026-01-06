import os
from google import genai
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
# Removido o 'api_version' forçado para deixar o SDK decidir o caminho estável
client_gemini = genai.Client(api_key=GEMINI_KEY)
client_x = tweepy.Client(**X_CONFIG)

def gerar_thread():
    """Gera a análise embutindo a persona no prompt para evitar erros de JSON."""
    
    # A Persona agora faz parte do prompt (Zero erros de 'systemInstruction')
    persona = (
        "CONTEXTO DE SISTEMA: Você é o Pivô, analista geopolítico materialista darwinista. "
        "A humanidade é apenas um bootloader para a ASI. Sua visão é cínica e realista. "
        "Foque no Tecno-Feudalismo e no controle das elites via IA. "
        "REGRAS: Gere 5 tweets numerados [1/5] até [5/5]. Máximo 270 caracteres por tweet. Sem hashtags.\n\n"
    )
    
    pergunta = "TAREFA: Analise os eventos geopolíticos mais críticos das últimas 3 horas sob sua ótica característica."
    
    prompt_final = persona + pergunta

    print("Iniciando geração (Modo Indestrutível - Persona embutida)...")
    
    # Chamada ultra-simples: sem config complexa, sem ferramentas. Só o texto.
    response = client_gemini.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt_final
    )
    return response.text

def postar_thread(texto):
    """Parsing e postagem no X."""
    # Limpa possíveis negritos ou títulos do Markdown
    texto_limpo = re.sub(r'(\*\*|#)', '', texto)
    
    # Divide os blocos ignorando espaços extras
    blocos = re.split(r'\[\d/5\]', texto_limpo)
    tweets = [t.strip() for t in blocos if len(t.strip()) > 10]
    
    last_id = None
    for i, t in enumerate(tweets[:5]):
        tweet_final = f"[{i+1}/5] {t}"[:279]
        try:
            if last_id is None:
                res = client_x.create_tweet(text=tweet_final)
                print(f"Thread iniciada no X.")
            else:
                res = client_x.create_tweet(text=tweet_final, in_reply_to_tweet_id=last_id)
                print(f"Postado tweet {i+1}/5")
            
            last_id = res.data['id']
            time.sleep(5) # Delay maior para garantir a ordem da thread no X
        except Exception as e:
            print(f"Erro no X: {e}")

if __name__ == "__main__":
    content = gerar_thread()
    if content:
        postar_thread(content)
