import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.connection import SessionLocal
from src.database.models import Regiao
from unidecode import unidecode

STATUS_MAP = {
    "ativo": 2, "ativos": 2, "fogo": 2, "queimando": 2,
    "extinto": 4, "extintos": 4, "apagado": 4, "controlado": 4
}


class DateExtractor:
    def __init__(self):
        # Mapa de números por extenso
        self.num_map = {
            "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "três": 3,
            "quatro": 4, "cinco": 5, "seis": 6, "sete": 7, "oito": 8, "nove": 9, "dez": 10
        }

        # Mapa de Meses
        self.month_map = {
            "janeiro": 1, "jan": 1,
            "fevereiro": 2, "fev": 2,
            "marco": 3, "março": 3, "mar": 3,
            "abril": 4, "abr": 4,
            "maio": 5, "mai": 5,
            "junho": 6, "jun": 6,
            "julho": 7, "jul": 7,
            "agosto": 8, "ago": 8,
            "setembro": 9, "set": 9,
            "outubro": 10, "out": 10,
            "novembro": 11, "nov": 11,
            "dezembro": 12, "dez": 12
        }

    def parse(self, text: str):
        today = datetime.now()
        text_clean = unidecode(text).lower()

        # 1. Detectar MÊS explícito (ex: "em outubro", "no mes de outubro")
        for mes_nome, mes_num in self.month_map.items():
            if re.search(r'\b' + mes_nome + r'\b', text_clean):

                # Lógica de Ano Inteligente:
                year = today.year
                if mes_num > today.month:
                    year = today.year - 1

                # Opcional: Tentar achar um ano explícito na frase (ex: "outubro de 2023")
                year_match = re.search(r'\b(20\d{2})\b', text_clean)
                if year_match:
                    year = int(year_match.group(1))

                # Retorna o dia 1º daquele mês
                return datetime(year, mes_num, 1)

        # 2. Detectar "últimos X dias/meses/anos"
        pattern = r"(?:nos?|nas?)?\s*últim[oa]s?\s+(?P<qtd>\w+)\s+(?P<unit>dias?|semanas?|meses?|anos?)"
        match = re.search(pattern, text_clean)

        if match:
            qtd_str = match.group("qtd")
            unit_str = match.group("unit")

            qtd = 1
            if qtd_str.isdigit():
                qtd = int(qtd_str)
            elif qtd_str in self.num_map:
                qtd = self.num_map[qtd_str]

            if "dia" in unit_str:
                return today - timedelta(days=qtd)
            elif "semana" in unit_str:
                return today - timedelta(weeks=qtd)
            elif "mes" in unit_str:
                return today - timedelta(days=30 * qtd)
            elif "ano" in unit_str:
                return today - timedelta(days=365 * qtd)

        # 3. Detectar singular simples
        if "ontem" in text_clean:
            return today - timedelta(days=1)
        if "hoje" in text_clean:
            return today
        if "ultima semana" in text_clean:
            return today - timedelta(days=7)
        if "ultimo mes" in text_clean:
            return today - timedelta(days=30)
        if "ultimo ano" in text_clean:
            return today - timedelta(days=365)

        return None


class EntityExtractor:
    def __init__(self):
        self.date_extractor = DateExtractor()
        self.region_map = {}
        self._load_knowledge()

    def _load_knowledge(self):
        print("  EntityExtractor: Carregando dicionários geográficos...")
        session: Session = SessionLocal()
        try:
            regioes = session.query(Regiao.nome_regiao).all()
            for (nome,) in regioes:
                chave = unidecode(nome).lower()
                self.region_map[chave] = nome
            print(f"  {len(self.region_map)} regiões carregadas do banco.")
        except Exception as e:
            print(f"  Erro ao carregar regiões: {e}")
        finally:
            session.close()

    def extract_entities(self, user_text: str) -> dict:
        text_clean = unidecode(user_text).lower()

        entities = {
            "bioma": None, "local": None, "status_id": None,
            "data_inicio": None, "data_fim": None,
            "order": "DESC", "limit": 1
        }

        # 1. Data
        start_date = self.date_extractor.parse(text_clean)
        if start_date:
            entities["data_inicio"] = start_date
            print(
                f"    DEBUG: Data identificada -> {start_date.strftime('%d/%m/%Y')}")

        # 2. Local
        sorted_keys = sorted(self.region_map.keys(), key=len, reverse=True)
        for key in sorted_keys:
            if key in text_clean:
                entities["local"] = self.region_map[key]
                break

        # 3. Status
        for word, s_id in STATUS_MAP.items():
            if word in text_clean:
                entities["status_id"] = s_id
                break

        # 4. Ordem e Limite
        if any(w in text_clean for w in ["menor", "menores", "minimo", "pior", "pequeno"]):
            entities["order"] = "ASC"

        tokens = text_clean.split()
        for token in tokens:
            val = None
            if token.isdigit():
                val = int(token)
            elif token in self.date_extractor.num_map:
                val = self.date_extractor.num_map[token]

            if val and 1 < val <= 50:
                entities["limit"] = val

        return entities
