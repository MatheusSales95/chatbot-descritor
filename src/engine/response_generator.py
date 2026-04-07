import requests


def gerar_texto_dinamico(pergunta_usuario: str, resultado_banco: str) -> str:
    OLLAMA_URL = "http://localhost:11434/api/generate"

    # O NOVO PROMPT INTELIGENTE (Flexível para Contagens e Listas)
    prompt_sistema = """Você é o DescrEVE, o assistente oficial do INPE.
Sua missão é transformar dados técnicos em respostas profissionais, naturais e precisas.

REGRAS ABSOLUTAS:
1. NUNCA invente cidades, datas, hectares ou durações. Use APENAS o que estiver em "Dados Brutos".
2. Se os Dados Brutos contiverem apenas um NÚMERO (uma contagem ou soma, ex: {'count': 5}), responda com uma frase simples e direta respondendo à pergunta do usuário. (Ex: "Foram encontrados 5 eventos ativos em Mato Grosso.").
3. Se os Dados Brutos contiverem uma LISTA com várias colunas (cidade, área, duração), crie tópicos em bullet points com as informações reais.
4. NUNCA mencione frases como "Dados Brutos" ou "INFORMAÇÃO DO BANCO".

"""

    contexto = f"Pergunta do Usuário: {pergunta_usuario}\n\nDados Brutos Retornados do Banco:\n{resultado_banco}"

    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": f"{prompt_sistema}\n\n{contexto}\n\nSua Resposta Oficial do INPE:",
        "stream": False,
        "options": {
            "temperature": 0.0  # Mantemos em 0 para ele NÃO inventar NADA
        }
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=500)
        if response.status_code == 200:
            return response.json().get('response', '').strip()
    except Exception as e:
        return f"Os dados extraídos do banco foram:\n\n{resultado_banco}"

    return f"Dados brutos obtidos:\n{resultado_banco}"
