import chromadb
import requests
import os
import re


class SQLGeneratorRAG:
    def __init__(self):
        # 1. Configura a conexão com o VectorDB (Chroma)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        db_path = os.path.join(base_dir, "data", "chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_collection(
            name="sql_examples")

        # 2. Configurações do Ollama (Qwen)
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "qwen2.5:1.5b"

        # 3. O "Mapa" do seu Banco (DDL Estrito)
        self.schema = """
        TABELAS E SUAS COLUNAS EXATAS (NUNCA INVENTE COLUNAS):
        - evento_fogo.focos_bdq_c2 (id_foco_bdq, data_hora_gmt, pais, estado, municipio, bioma, frp, precipitacao, numero_dias_sem_chuva, geometria) -> ATENÇÃO: NÃO POSSUI id_evento!
        - evento_fogo.evento_fogo (id_evento, qtd_frente, duracao, data_min, data_max, max_frp, area_acm, id_status, risco_medio, geom) -> ATENÇÃO: NÃO POSSUI municipio, estado ou data_hora_gmt!
        - evento_fogo.frente_fogo (id_frente, id_evento, geom)
        - evento_fogo.status_evento (id_status, status_nome)
        - evento_fogo.regiao (id_regiao, nome_regiao, id_tipo_reg)
        - evento_fogo.evento_regiao (id_evento, id_regiao)
        
        REGRAS DE RELACIONAMENTO (CRÍTICAS - LEIA COM ATENÇÃO):
        1. A tabela `focos_bdq_c2` NÃO TEM `id_evento`. Para conectar focos a eventos, use OBRIGATORIAMENTE: JOIN evento_fogo.frente_fogo ff ON ST_Intersects(f.geometria, ff.geom) JOIN evento_fogo.evento_fogo e ON ff.id_evento = e.id_evento.
        2. Para saber a cidade/estado de um EVENTO, NUNCA use a tabela focos. USE SEMPRE: JOIN evento_fogo.evento_regiao er ON ef.id_evento = er.id_evento JOIN evento_fogo.regiao r ON er.id_regiao = r.id_regiao.
        3. No SELECT, traga APENAS as colunas textuais e numéricas pedidas. NUNCA, SOB NENHUMA HIPÓTESE, selecione as colunas `geom` ou `geometria`. Elas quebram o sistema!
        4. "Maiores eventos" sempre significa ordenar pela área (ORDER BY area_acm DESC).
        """

    def retrieve_examples(self, question: str, n_results: int = 4) -> str:
        """Busca as X perguntas mais parecidas no banco vetorial."""
        results = self.collection.query(
            query_texts=[question],
            n_results=n_results
        )

        examples_text = ""
        if results and results['documents'] and results['documents'][0]:
            for idx, doc in enumerate(results['documents'][0]):
                sql = results['metadatas'][0][idx]['sql']
                examples_text += f"Exemplo {idx+1}:\nPergunta: {doc}\nSQL: {sql}\n\n"
        return examples_text

    def generate_sql(self, question: str) -> str:
        """Constrói o Prompt (RAG) e pede ao LLM para gerar a query final."""

        # Puxa os exemplos do ChromaDB
        examples = self.retrieve_examples(question)

        # Monta o Prompt Gigante
        prompt = f"""Você é um Especialista PostgreSQL e PostGIS estrito.
Sua única tarefa é gerar uma consulta SQL válida para responder à pergunta do usuário.

REGRAS ABSOLUTAS (O DESCUMPRIMENTO CAUSARÁ ERRO):
1. Retorne APENAS o código SQL puro. Nada de explicações.
2. USE APENAS AS COLUNAS E TABELAS LISTADAS NO SCHEMA. NUNCA invente colunas.
3. SEMPRE use o prefixo do schema nas tabelas (ex: evento_fogo.regiao).
4. NUNCA adicione filtros de data ou status que o usuário não pediu explicitamente na pergunta.
5. Se o usuário falar o nome de uma cidade/estado, use "ILIKE '%nome%'" para buscar na tabela regiao.

SCHEMA DO BANCO (SUA ÚNICA VERDADE):
{self.schema}

EXEMPLOS SEMELHANTES:
{examples}

Pergunta do Usuário: {question}
SQL:"""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0  # Temperatura ZERO = Precisão e zero alucinação
            }
        }

        try:
            print("Consultando Qwen para gerar SQL (RAG Ativado)...")
            response = requests.post(
                self.ollama_url, json=payload, timeout=500)
            if response.status_code == 200:
                generated_text = response.json().get('response', '').strip()

                # O LLM costuma colocar a query entre ```sql ... ```. Vamos limpar isso com Regex:
                sql_match = re.search(
                    r'```sql\s*(.*?)\s*```', generated_text, re.DOTALL | re.IGNORECASE)
                if sql_match:
                    return sql_match.group(1).strip()

                # Se ele não usou a marcação, retorna o texto limpando possíveis formatações chatas
                return generated_text.replace('```', '').strip()

            return "ERRO: Falha na API do Ollama."
        except Exception as e:
            print(f"Erro Crítico ao gerar SQL: {e}")
            return "ERRO: Exceção no código de geração."


# --- BLOCO DE TESTE RÁPIDO ---
if __name__ == "__main__":
    gerador = SQLGeneratorRAG()

    pergunta_teste = "quantos eventos ativos em sao paulo"

    print(f"\nUsuário perguntou: '{pergunta_teste}'")
    sql_gerado = gerador.generate_sql(pergunta_teste)

    print("\nSQL GERADO PELO QWEN:")
    print(sql_gerado)
