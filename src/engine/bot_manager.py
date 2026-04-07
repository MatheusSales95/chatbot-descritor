from src.engine.sql_generator_rag import SQLGeneratorRAG
from src.engine.response_generator import gerar_texto_dinamico
from src.database.connection import SessionLocal
from sqlalchemy import text
import traceback


class BotManager:
    def __init__(self):
        print("Inicializando BotManager com Arquitetura Text-to-SQL (RAG + Qwen)...")
        # Instanciamos nosso novo gerador inteligente
        self.sql_rag = SQLGeneratorRAG()

    def process_message(self, message: str) -> dict:
        """
        Fluxo principal: Pergunta -> RAG (Qwen) -> SQL -> Banco (PostGIS) -> Resumo (Qwen)
        """
        print(f"\nDescrEVE processando: '{message}'")

        try:
            # 1. RAG: Qwen gera o SQL baseado na pergunta e no ChromaDB
            query_sql = self.sql_rag.generate_sql(message)
            print(f"🔍 SQL Gerado pela IA:\n{query_sql}")

            # Trava de segurança: Se a IA alucinar e não gerar um SELECT, abortamos
            if not query_sql.strip().upper().startswith("SELECT"):
                return {
                    "response": "Desculpe, a inteligência artificial não conseguiu formular uma busca válida para essa pergunta. Tente ser mais específico sobre o estado ou tipo de evento.",
                    "intent": "fallback",
                    "confidence": 0.0
                }

            # 2. Executa no Banco de Dados de forma segura
            dados_brutos = self._execute_query(query_sql)

            # 3. GERAÇÃO DINÂMICA: Passamos o resultado bruto para o Qwen formatar lindamente
            resposta_final = gerar_texto_dinamico(message, dados_brutos)

            return {
                "response": resposta_final,
                "intent": "text_to_sql_rag",
                "confidence": 0.95
            }

        except Exception as e:
            print(f"ERRO CRÍTICO NO BOT MANAGER:\n{traceback.format_exc()}")
            return {
                "response": "Ocorreu um erro técnico inesperado ao processar sua solicitação no servidor.",
                "intent": "error",
                "confidence": 0.0
            }

    def _execute_query(self, query: str) -> str:
        """
        Executa a query gerada pelo LLM de forma segura e formata o retorno.
        """
        try:
            with SessionLocal() as db:
                # O text() do SQLAlchemy protege parcialmente contra algumas injeções
                resultado = db.execute(text(query))

                if resultado.returns_rows:
                    # Trava de segurança 2: Limitamos a 10 resultados para o Qwen não travar lendo milhares de linhas
                    linhas = resultado.fetchmany(10)

                    if not linhas:
                        return "INFORMAÇÃO DO BANCO: Nenhum dado foi encontrado para os filtros solicitados."

                    # Formata o resultado em um formato fácil para o LLM ler (estilo dicionário/JSON)
                    colunas = resultado.keys()
                    texto_resultado = f"Busca realizada. Colunas retornadas: {', '.join(colunas)}\nResultados (Máximo 10 exibidos):\n"

                    for linha in linhas:
                        # Converte a linha do banco em dicionário
                        linha_dict = dict(zip(colunas, linha))

                        # TRAVA DE SEGURANÇA: Remove dados binários espaciais que fritam o LLM
                        linha_dict.pop('geom', None)
                        linha_dict.pop('geometria', None)

                        texto_resultado += str(linha_dict) + "\n"

                    return texto_resultado
                else:
                    return "Query executada, mas não é uma consulta de retorno de dados."

        except Exception as e:
            erro_msg = str(e)
            print(f"Erro do PostgreSQL ao rodar a query gerada: {erro_msg}")
            # Retornamos o erro do banco para o Qwen, assim ele pode até "explicar" que a busca falhou
            return "ERRO NO BANCO DE DADOS: A consulta gerada possui erro de sintaxe ou coluna inexistente."
