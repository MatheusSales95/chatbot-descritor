from sqlalchemy import text
from src.database.connection import SessionLocal


class SQLGenerator:
    def __init__(self):
        # Usamos JOINs para unir todas as informações espalhadas nas tabelas de dimensão
        self.base_from = """
            evento_fogo.evento_fogo ef
            LEFT JOIN evento_fogo.status_evento se ON ef.id_status = se.id_status
            LEFT JOIN evento_fogo.evento_regiao er ON ef.id_evento = er.id_evento
            LEFT JOIN evento_fogo.regiao r ON er.id_regiao = r.id_regiao
            LEFT JOIN evento_fogo.tipo_regiao tr ON r.id_tipo_reg = tr.id_tipo_reg
            LEFT JOIN evento_fogo.evento_tipo_fogo etf ON ef.id_evento = etf.id_evento
            LEFT JOIN evento_fogo.tipo_fogo tf ON etf.id_tipo = tf.id_tipo
        """

    def _aplicar_filtros(self, entities: dict) -> tuple[str, dict]:
        """
        Lê as entidades extraídas e monta a cláusula WHERE conectando as tabelas corretas.
        """
        filtros = []
        params = {}

        # 1. Localização (Busca na tabela de região)
        loc = entities.get("estado") or entities.get(
            "municipio") or entities.get("localizacao")
        if loc:
            filtros.append("r.nome_regiao ILIKE :localizacao")
            params["localizacao"] = f"%{loc}%"

        # 2. Status (Ativo, Extinto - na tabela status_evento)
        if "status" in entities:
            filtros.append("se.status_nome ILIKE :status")
            params["status"] = f"%{entities['status']}%"

        # 3. Tipo de Evento (na tabela tipo_fogo)
        if "tipo_evento" in entities:
            filtros.append("tf.tipo_nome ILIKE :tipo_evento")
            params["tipo_evento"] = f"%{entities['tipo_evento']}%"

        # 4. Tipo de Área (Bioma, Terra Indígena - na tabela tipo_regiao)
        if "tipo_area" in entities:
            filtros.append("tr.tipo_nome ILIKE :tipo_area")
            params["tipo_area"] = f"%{entities['tipo_area']}%"

        # 5. Tempo sem chuva (na tabela evento_fogo)
        if "tempo_sem_chuva" in entities:
            filtros.append("ef.max_dias_sem_chuva >= :tempo_sem_chuva")
            # Extrai só o número da entidade se vier como "10 dias"
            apenas_numeros = ''.join(
                filter(str.isdigit, str(entities["tempo_sem_chuva"])))
            params["tempo_sem_chuva"] = int(
                apenas_numeros) if apenas_numeros else 0

        # 6. Tempo de duração do evento (na tabela evento_fogo - tipo interval)
        if "tempo_duracao" in entities:
            filtros.append("ef.duracao >= CAST(:tempo_duracao AS INTERVAL)")
            apenas_numeros = ''.join(
                filter(str.isdigit, str(entities["tempo_duracao"])))
            params["tempo_duracao"] = f"{apenas_numeros} days" if apenas_numeros else "0 days"

        # 7. Período / Data (na tabela evento_fogo)
        if "periodo" in entities:
            filtros.append("ef.data_max >= CAST(:periodo AS TIMESTAMP)")
            params["periodo"] = entities["periodo"]

        # Monta a string final do WHERE (usa 1=1 se não houver filtros)
        where_clause = " AND ".join(filtros) if filtros else "1=1"
        return where_clause, params

    def _count_events(self, entities: dict) -> str:
        """ Intenção: Contar a quantidade de eventos """
        where_clause, params = self._aplicar_filtros(entities)
        # Usamos COUNT(DISTINCT ef.id_evento) para evitar duplicidade causada pelos JOINs
        query = f"SELECT COUNT(DISTINCT ef.id_evento) FROM {self.base_from} WHERE {where_clause}"

        try:
            with SessionLocal() as db:
                resultado = db.execute(text(query), params).scalar()
            return f"RESULTADO EXATO DO BANCO: Encontrados {resultado} eventos que correspondem a esta busca."
        except Exception as e:
            print(f"Erro SQL (Count): {e}")
            return "Erro ao consultar a quantidade no banco de dados."

    def _calculate_area(self, entities: dict) -> str:
        """ Intenção: Somar a área total afetada """
        where_clause, params = self._aplicar_filtros(entities)
        query = f"SELECT SUM(ef.area_acm) FROM {self.base_from} WHERE {where_clause}"

        try:
            with SessionLocal() as db:
                resultado = db.execute(text(query), params).scalar()
                resultado = round(resultado, 2) if resultado else 0
            return f"RESULTADO EXATO DO BANCO: A área total acumulada (area_acm) é de {resultado} hectares."
        except Exception as e:
            print(f"Erro SQL (Area): {e}")
            return "Erro ao consultar a área no banco de dados."

    def _ranking_eventos(self, entities: dict) -> str:
        """ Intenção: Listar os eventos trazendo TODOS os detalhes possíveis """
        where_clause, params = self._aplicar_filtros(entities)

        # Agora buscamos 8 colunas diferentes de várias tabelas!
        query = f"""
            SELECT 
                r.nome_regiao, 
                ef.area_acm, 
                se.status_nome,
                tf.tipo_nome,
                tr.tipo_nome as tipo_area,
                ef.duracao,
                ef.max_dias_sem_chuva,
                ef.data_max
            FROM {self.base_from} 
            WHERE {where_clause} 
            ORDER BY ef.area_acm DESC NULLS LAST LIMIT 5
        """

        try:
            with SessionLocal() as db:
                linhas = db.execute(text(query), params).fetchall()
                if not linhas:
                    return "INFORMAÇÃO DO BANCO: Nenhum evento encontrado com esses filtros."

                texto_ranking = "INFORMAÇÃO DO BANCO (Resuma esses detalhes para o usuário de forma natural):\n\n"

                for i, linha in enumerate(linhas, 1):
                    # Tratamento caso algum dado venha vazio (NULL) do banco
                    regiao = linha[0] or "Não identificada"
                    area = round(linha[1], 2) if linha[1] else 0
                    status = linha[2] or "Desconhecido"
                    tipo_evento = linha[3] or "Não especificado"
                    tipo_area = linha[4] or "Não especificada"
                    duracao = linha[5] or "Não registrada"
                    dias_sem_chuva = linha[6] or 0
                    data_max = linha[7] or "Desconhecida"

                    # Monta a "ficha" do evento para o Qwen ler
                    texto_ranking += (
                        f"Evento {i}:\n"
                        f"- Localização: {regiao}\n"
                        f"- Área Afetada: {area} hectares\n"
                        f"- Status Atual: {status}\n"
                        f"- Tipo de Fogo: {tipo_evento}\n"
                        f"- Tipo de Área: {tipo_area}\n"
                        f"- Tempo de Duração: {duracao}\n"
                        f"- Dias sem chuva na região: {dias_sem_chuva} dias\n"
                        f"- Data do último registro: {data_max}\n"
                        "------------------------\n"
                    )
                return texto_ranking
        except Exception as e:
            print(f"Erro SQL (Ranking): {e}")
            return "Erro ao buscar os detalhes dos eventos no banco de dados."
